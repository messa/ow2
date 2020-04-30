from aiohttp import ClientSession, TCPConnector, Fingerprint
from aiohttp.resolver import AsyncResolver
from asyncio import TimeoutError, CancelledError, shield, sleep, wait_for
from datetime import datetime, timedelta
from itertools import count
from pprint import pformat
from pytz import utc
from reprlib import repr as smart_repr
from socket import getfqdn
from ssl import SSLError, SSLCertVerificationError
from time import monotonic as monotime
from time import time

from .util import parse_datetime, add_log_context, get_logger


logger = get_logger(__name__)

_log_target_id_counter = count()

dns_timeout = 15


async def check_target(session, conf, target, send_report_semaphore):
    with add_log_context(f't{next(_log_target_id_counter):02d}'):
        logger.debug('check_target: %s', target)
        interval = target.interval or conf.default_interval
        interval_s = interval.total_seconds()
        check_counter = count()
        while True:
            with add_log_context(f'ch{next(check_counter):05d}'):
                await check_target_once(
                    conf, target, interval_s,
                    send_report=lambda report: send_report(
                        session, conf, report, send_report_semaphore))
            logger.debug('Sleeping for %d s', interval_s)
            await sleep(interval_s)


async def check_target_once(conf, target, interval_s, send_report):
    try:
        logger.debug('check_target_once: %s', target)
        report = {
            'date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'label': generate_label(conf, target),
            'state': {
                'url': target.url,
                'interval': {
                    '__value': interval_s,
                    '__unit': 'seconds',
                },
                'by_ip': {},
                'error': {
                    '__value': None,
                    '__check': {'state': 'green'},
                },
            },
        }
        try:
            hostname, ips = await get_url_ip_addresses(target.url)
        except CancelledError as e:
            raise e
        except Exception as e:
            report['state']['error'] = {
                '__value': f'Failed to resolve hostname of {target.url!r}: {e!r}',
                '__check': {'state': 'red'},
            }
        else:
            if not ips:
                report['state']['error'] = {
                    '__value': f'Hostname {hostname!r} does not resolve to IP addresses',
                    '__check': {'state': 'red'},
                }
            else:
                for n, ip in enumerate(ips):
                    with add_log_context(f'ip{n:02}'):
                        await check_target_ip(conf, target, report, hostname, ip)
        report['state']['watchdog'] = {
            '__watchdog': {
                'deadline': int((time() + interval_s + 15) * 1000),
            },
        }
        try:
            await wait_for(shield(send_report(report)), 1)
        except TimeoutError:
            logger.debug('send_report is taking too long, not waiting for it')
    except CancelledError as e:
        logger.exception('check_target_once cancelled (%r); target: %s', e, target)
        raise e
    except Exception as e:
        logger.exception('check_target_once failed: %r; target: %s', e, target)
        raise Exception(f'check_target_once failed: {e!r}') from None


async def check_target_ip(conf, target, report, hostname, ip):
    logger.debug('Checking IP address %s', ip)
    ip_report = {
        'error': {
            '__value': None,
            '__check': {
                'state': 'green',
            },
        },
    }
    try:
        ip_report['reverse_record'] = await get_ip_reverse(ip)
    except CancelledError as e:
        logger.debug('get_ip_reverse cancelled')
        raise e
    except ReverseLookupError as e:
        logger.debug('get_ip_reverse ReverseLookupError: %s', e)
        ip_report['reverse_record'] = None
        ip_report['reverse_record_error'] = str(e)
    start_time = monotime()
    try:
        conn = CustomTCPConnector(resolver=CustomResolver(hostname, ip))
        async with ClientSession(connector=conn) as session:
            start_time = monotime()
            async with session.get(target.url) as response:
                status_ok = response.status == 200
                ip_report['status_code'] = {
                    '__value': response.status,
                    '__check': {
                        'state': 'green' if status_ok else 'red',
                    },
                }
                data = await response.read()
                duration = monotime() - start_time
                duration_threshold = target.duration_threshold or conf.default_duration_threshold
                duration_ok = timedelta(seconds=duration) <= duration_threshold
                ip_report['duration'] = {
                    '__value': duration,
                    '__unit': 'seconds',
                    '__check': {
                        'state': 'green' if duration_ok else 'red',
                    },
                }
                ip_report['response_size'] = {
                    '__value': len(data),
                    '__unit': 'bytes',
                }
                ip_report['redirect_count'] = len(response.history)
                ip_report['final_url'] = str(response.url)
                ip_report['ssl_certificate'] = get_ssl_cert_report(conn.get_last_cert())
                # try:
                #     ip_report['response_preview'] = data.decode()[:100]
                # except Exception:
                #     ip_report['response_preview'] = str(data)[:100]
                logger.debug(
                    'GET %r -> %s %s in %.3f s',
                    target.url, response.status, smart_repr(data), duration)
                if status_ok and target.check_response_contains:
                    present = to_bytes(target.check_response_contains) in data
                    ip_report['check_response_contains'] = {
                        'content': target.check_response_contains,
                        'present': {
                            '__value': present,
                            '__check': {
                                'state': 'green' if present else 'red',
                            },
                        },
                    }
    except CancelledError as e:
        logger.info('GET %r via %s cancelled: %r', target.url, ip, e)
        raise e
    except Exception as e:
        logger.info('GET %r via %s failed: %r', target.url, ip, e)
        if isinstance(e, SSLError):
            if 'certificate has expired' in str(e):
                msg = 'SSL certificate has expired'
            else:
                msg = f'SSLError: {e}'
        else:
            msg = str(e) or repr(e)
        ip_report['error'] = {
            '__value': msg,
            '__check': {
                'state': 'red',
            },
        }
    ip_report.setdefault('duration', {'__value': monotime() - start_time})
    report['state']['by_ip'][ip] = ip_report


class CustomTCPConnector (TCPConnector):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__fingerprint_obj = _FingerprintObj()

    def _get_ssl_context(self, req):
        if req.is_ssl():
            return self._make_ssl_context(True)
        else:
            return None

    def _get_fingerprint(self, req):
        return self.__fingerprint_obj

    def get_last_cert(self):
        return self.__fingerprint_obj.last_cert


class _FingerprintObj:

    def __init__(self):
        self.last_cert = None

    def check(self, transport):
        if not transport.get_extra_info('sslcontext'):
            return
        sslobj = transport.get_extra_info('ssl_object')
        self.last_cert = sslobj.getpeercert(binary_form=False)


def get_ssl_cert_report(cert):
    logger.debug('cert: %r', cert)
    if cert is None:
        return None
    if not cert:
        # Docs: "If the certificate was not validated, the dict is empty."
        raise Exception('Certificate not validated')
    report = {k: _ssl_cert_value(v) for k, v in cert.items()}

    expire_dt = parse_datetime(report['notAfter'])
    now = utc.localize(datetime.utcnow())
    if expire_dt < now + timedelta(days=10):
        expire_state = 'red'
    elif expire_dt < now + timedelta(days=20):
        expire_state = 'yellow'
    else:
        expire_state = 'green'

    report['expire_date'] = {
        '__value': expire_dt.isoformat(),
        '__check': {
            'state': expire_state,
        },
    }

    return report


def _ssl_cert_value(obj):
    '''
    Convert stuff like ((('commonName', 'messa.cz'),),) to something more readable
    '''
    # TODO: redo this :)
    while isinstance(obj, tuple) and len(obj) == 1:
        obj, = obj
    if isinstance(obj, tuple):
        parts = [_ssl_cert_value(v) for v in obj]
        #parts = ['[{}]'.format(p) if isinstance(p, tuple) else p for p in parts]
        if len(parts) == 2:
            k, v = parts
            if '=' not in k and '=' not in v:
                return '{}={}'.format(k, v)
        return ','.join('({})'.format(part) for part in parts)
    return str(obj)


def generate_label(conf, target):
    label = {
        'agent': 'http_check',
        'host': getfqdn(),
        'url': target.url,
    }
    for src in conf.default_label, target.label:
        for k, v in src.items():
            if not v:
                label.pop(k, None)
            else:
                label[k] = v
    return label


def to_bytes(s):
    if isinstance(s, str):
        s = s.encode()
    assert isinstance(s, bytes)
    return s


async def get_url_ip_addresses(url):
    from aiodns import DNSResolver
    from socket import AF_INET
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname
    resolver = DNSResolver()
    try:
        r = await wait_for(resolver.gethostbyname(hostname, AF_INET), dns_timeout)
    except CancelledError as e:
        raise e
    except TimeoutError:
        raise Exception(f'gethostbyname({hostname!r}, AF_INET) timed out after {dns_timeout} s')
    except Exception as e:
        raise Exception(f'gethostbyname({hostname!r}, AF_INET) failed: {e!r}')
    logger.debug('get_url_ip_addresses: %r -> %r -> %r', url, hostname, r.addresses)
    return hostname, r.addresses


class ReverseLookupError (Exception):
    pass


async def get_ip_reverse(ip):
    from aiodns import DNSResolver
    from aiodns.error import DNSError
    resolver = DNSResolver()
    try:
        return await wait_for(resolver.gethostbyaddr(ip), dns_timeout)
    except CancelledError as e:
        raise e
    except TimeoutError:
        raise ReverseLookupError(f'gethostbyaddr({ip!r}) timed out after {dns_timeout} s')
    except DNSError as e:
        raise ReverseLookupError(str(e))
    except Exception as e:
        raise ReverseLookupError(f'gethostbyaddr({ip!r}) failed: {e!r}')


class CustomResolver:

    def __init__(self, hostname, ip):
        self._parent = AsyncResolver()
        self._hostname = hostname
        self._ip = ip

    async def resolve(self, host, port, family):
        from socket import AI_NUMERICHOST
        if host == self._hostname:
            return [
                {
                    'hostname': host,
                    'host': self._ip,
                    'port': port,
                    'family': 0,
                    'proto': 0,
                    'flags': AI_NUMERICHOST,
                }
            ]
        else:
            result = await self._parent.resolve(host, port, family)
            logger.debug('resolve(%r, %r, %r) -> %r', host, port, family, result)
            return result


async def send_report(session, conf, report, send_report_semaphore):
    try:
        async with send_report_semaphore:
            logger.debug('Sending report to %s', conf.report_url)
            headers = {}
            if conf.report_token:
                headers['Authorization'] = 'Bearer ' + conf.report_token
            async with session.post(conf.report_url, json=report, headers=headers) as r:
                r.raise_for_status()
                logger.debug('Report sent successfully')
    except CancelledError as e:
        raise e
    except Exception as e:
        logger.warning('Failed to send report to %s: %r', conf.report_url, e)
        if isinstance(e, TypeError):
            logger.debug('Report:\n%s', pformat(report, width=200))
