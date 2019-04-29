from aiohttp import ClientSession, TCPConnector
from aiohttp.resolver import AsyncResolver
from asyncio import Semaphore, create_task, sleep
from datetime import datetime, timedelta
from logging import getLogger
from reprlib import repr as smart_repr
from socket import getfqdn
from ssl import SSLError, SSLCertVerificationError
from time import monotonic as monotime
from time import time


logger = getLogger(__name__)


async def check_target(session, conf, target):
    logger.debug('check_target: %s', target)
    interval = target.interval or conf.default_interval
    interval_s = interval.total_seconds()
    while True:
        #async with session.get(target.url) as r:
        #    logger.debug('GET %s -> %r', target.url, r)
        await check_target_once(session, conf, target, interval_s)
        logger.debug('Sleeping for %d s', interval_s)
        await sleep(interval_s)


async def check_target_once(session, conf, target, interval_s):
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
                for ip in ips:
                    await check_target_ip(conf, target, report, hostname, ip)
        report['state']['watchdog'] = {
            '__watchdog': {
                'deadline': int((time() + interval_s + 15) * 1000),
            },
        }
        create_task(send_report(session, conf, report))
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
    start_time = monotime()
    try:
        conn = TCPConnector(resolver=CustomResolver(hostname, ip))
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
                # try:
                #     ip_report['response_preview'] = data.decode()[:100]
                # except Exception:
                #     ip_report['response_preview'] = str(data)[:100]
                logger.debug(
                    'GET %r -> %s %s in %.3f s',
                    target.url, response.status, smart_repr(data), duration)
                if target.check_response_contains:
                    present = to_bytes(check_response_contains) in data
                    ip_report['check_response_contains'] = {
                        'content': target.check_response_contains,
                        'present': {
                            '__value': present,
                            '__check': {
                                'state': 'green' if present else 'red',
                            },
                        },
                    }
    except Exception as e:
        logger.info('GET %r via %s failed: %r', target.url, ip, e)
        if isinstance(e, SSLError):
            if 'certificate has expired' in str(e):
                msg = 'SSL certificate has expired'
            else:
                msg = f'SSLError: {e}'
        else:
            msg = str(e)
        ip_report['error'] = {
            '__value': msg,
            '__check': {
                'state': 'red',
            },
        }
    ip_report.setdefault('duration', {'__value': monotime() - start_time})
    report['state']['by_ip'][ip] = ip_report


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
    r = await resolver.gethostbyname(hostname, AF_INET)
    logger.debug('get_url_ip_addresses: %r -> %r -> %r', url, hostname, r.addresses)
    return hostname, r.addresses


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


send_report_semaphore = Semaphore(2)


async def send_report(session, conf, report):
    try:
        async with send_report_semaphore:
            logger.debug('Sending report to %s', conf.report_url)
            headers = {}
            if conf.report_token:
                headers['Authorization'] = 'Bearer ' + conf.report_token
            async with session.post(conf.report_url, json=report, headers=headers) as r:
                r.raise_for_status()
                logger.debug('Report sent successfully')
    except Exception as e:
        logger.warning('Failed to send report to %s: %r', conf.report_url, e)
