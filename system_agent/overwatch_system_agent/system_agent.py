import argparse
from datetime import datetime
from datetime import timedelta
import logging
import os
import psutil
import requests
from socket import getfqdn
import sys
from time import monotonic as monotime
from time import time, sleep

from .configuration import Configuration
from .helpers import setup_logging, setup_log_file


logger = logging.getLogger(__name__)

default_sleep_interval = 15
default_report_timeout = 10

rs = requests.session()


def system_agent_main():
    p = argparse.ArgumentParser()
    p.add_argument('--verbose', '-v', action='count')
    p.add_argument('--conf')
    args = p.parse_args()
    conf = Configuration(args.conf)
    try:
        setup_logging(verbosity=args.verbose)
        setup_log_file(conf.log_file_path)
        logger.debug('System agent starting')
        run_system_agent(conf)
    except BaseException as e:
        logger.exception('System agent failed: %r', e)
        sys.exit('ERROR: {!r}'.format(e))


def run_system_agent(conf):
    #sleep_interval = conf.sleep_interval or default_sleep_interval
    sleep_interval = 15
    while True:
        run_system_agent_iteration(conf, sleep_interval)
        sleep(sleep_interval)


def run_system_agent_iteration(conf, sleep_interval):
    report_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    t0 = monotime()
    report_state = gather_state(conf)
    duration = monotime() - t0
    report_state['duration'] = {
        '__value': duration,
        '__unit': 'seconds',
    }

    # add watchdog
    #wd_interval = conf.watchdog_interval or sleep_interval + 30
    wd_interval = sleep_interval + 30
    report_state['watchdog'] = {
        '__watchdog': {
            'deadline': int((time() + wd_interval) * 1000),
        },
    }

    report_data = {
        'label': generate_label(conf),
        'date': report_date,
        'state': report_state,
    }

    try:
        r = rs.post(conf.report_url,
            json=report_data,
            headers={'Authorization': 'token ' + conf.report_token},
            timeout=default_report_timeout)
        logger.debug('Report response: %s', r.text[:100])
        r.raise_for_status()
    except Exception as e:
        logger.error('Failed to post report to %r: %r', conf.report_url, e)
        logger.info('Report token: %s...%s', conf.report_token[:3], conf.report_token[-3:])
        logger.info('Report data: %r', report_data)


def generate_label(conf):
    label = {
        'agent': 'system',
        'host': getfqdn(),
    }
    for k, v in conf.label.items():
        if not v:
            label.pop(k, None)
        else:
            label[k] = v
    return label


def gather_state(conf):
    return {
        'cpu': gather_cpu(),
        'load': gather_load(),
        'uptime': gather_uptime(),
        'volumes': gather_volumes(),
        'memory': gather_memory(),
        'swap': gather_swap(),
        'public_source_ip4': gather_public_source_ip4(),
        'public_source_ip6': gather_public_source_ip6(),
    }


def value(value, counter=None, unit=None, check_state=None):
    '''
    Helper function to generate the report value metadata fragment.
    '''
    data = {
        '__value': value,
    }
    if counter:
        data['__counter'] = True
    if unit:
        data['__unit'] = unit
    if check_state:
        data.setdefault('__check', {})
        data['__check']['state'] = check_state
    return data


def gather_public_source_ip4():
    try:
        r = rs.get('https://ip4.messa.cz/', timeout=10)
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        logger.warning('Failed to retrieve public_source_ip4: %r', e)
        return None


def gather_public_source_ip6():
    try:
        r = rs.get('https://ip6.messa.cz/', timeout=10)
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        # log as just info, because some hosts do not have IPv6 configured
        logger.info('Failed to retrieve public_source_ip6: %r', e)
        return None


def gather_load():
    data = {
        '01m': round(os.getloadavg()[0], 2),
        '05m': round(os.getloadavg()[1], 2),
        '15m': round(os.getloadavg()[2], 2)
    }
    return data


def gather_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds = uptime_seconds))
    except FileNotFoundError as e:
        logger.debug('Cannot determine uptime: %s', e)
        return None
    data = {
        'seconds': round(uptime_seconds, 0),
        'string': uptime_string
    }
    return data


def gather_cpu():
    ct = psutil.cpu_times()
    cs = psutil.cpu_stats()
    data = {
        'count': {
            'logical': psutil.cpu_count(logical=True),
            'physical': psutil.cpu_count(logical=False),
        },
        'times': {},
        'stats': {
            'ctx_switches': value(cs.ctx_switches, counter=True),
            'interrupts': value(cs.interrupts, counter=True),
            'soft_interrupts': value(cs.soft_interrupts, counter=True),
            'syscalls': value(cs.syscalls, counter=True),
        },
    }
    for k in 'user', 'system', 'idle', 'iowait':
        try:
            data['times'][k] = value(getattr(ct, k), counter=True)
        except AttributeError:
            pass
    return data


def gather_volumes():
    percent_red_threshold = 92
    free_bytes_red_threshold = 2 * 2**30 # 2 GB
    volumes = {}
    for p in psutil.disk_partitions():
        usage = psutil.disk_usage(p.mountpoint)

        if usage.total >= free_bytes_red_threshold * 4 and usage.free < free_bytes_red_threshold:
            usage_free_state = 'red'
        else:
            usage_free_state = 'green'

        if usage.percent >= percent_red_threshold:
            usage_percent_state = 'red'
        else:
            usage_percent_state = 'green'

        volumes[p.mountpoint] = {
            'mountpoint': p.mountpoint,
            'device': p.device,
            'fstype': p.fstype,
            'opts': p.opts,
            'usage': {
                'total_bytes': value(usage.total, unit='bytes'),
                'used_bytes': value(usage.used, unit='bytes'),
                'free_bytes': value(usage.free, unit='bytes', check_state=usage_free_state),
                'percent': value(usage.percent, unit='percents', check_state=usage_percent_state),
            }
        }
    return volumes


def gather_memory():
    mem = psutil.virtual_memory()
    return {
        'total_bytes': value(mem.total, unit='bytes'),
        'available_bytes': value(mem.available, unit='bytes'),
    }


def gather_swap():
    sw = psutil.swap_memory()
    return {
        'total_bytes': value(sw.total, unit='bytes'),
        'used_bytes': value(sw.used, unit='bytes'),
        'free_bytes': value(sw.free, unit='bytes'),
        'percent': value(sw.percent, unit='percents', check_state='red' if sw.percent > 80 else 'green'),
    }
