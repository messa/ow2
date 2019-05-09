from datetime import datetime, timedelta
from itertools import count
import os
import re
from reprlib import repr as smart_repr
from socket import getfqdn
from time import monotonic as monotime
from time import time

from .report import send_report
from .util import get_logger, add_log_context, create_task


logger = get_logger(__name__)

_log_target_id_counter = count()


async def check_target(session, conf, target, send_report_semaphore):
    with add_log_context('t{:02d}'.format(next(_log_target_id_counter))):
        logger.debug('check_target: %s', target)
        check_counter = count()
        while True:
            with add_log_context('ch{:05d}'.format(next(check_counter))):
                await check_target_once(session, conf, target, send_report_semaphore)


async def check_target_once(session, conf, target, send_report_semaphore):
    try:
        logger.debug('check_target_once: %s', target)
        report = {
            'label': generate_label(conf, target),
            'state': {
                'address': target.address,
            },
        }
        await run_ping(report, target)
        #logger.debug('report: %r', report)
        report['date'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        report['state']['watchdog'] = {
            '__watchdog': {
                'deadline': int((time() + 90) * 1000),
            }
        }
        create_task(send_report(session, conf, report, send_report_semaphore))
    except Exception as e:
        logger.exception('check_target_once failed: %r; target: %s', e, target)
        raise Exception('check_target_once failed: {!r}'.format(e)) from None


async def run_ping(report, target):
    from asyncio import create_subprocess_exec
    from subprocess import DEVNULL, PIPE, STDOUT
    from reprlib import repr as smart_repr
    cmd = 'ping -c 60 -i 1 -n ip4.messa.cz'.split()
    p = await create_subprocess_exec(*cmd, stdin=DEVNULL, stdout=PIPE, stderr=PIPE)
    logger.debug('Started ping process pid %s', p.pid)
    stdout, stderr = await p.communicate()
    #logger.debug('ping stdout: %s stderr: %s', smart_repr(stdout), smart_repr(stderr))
    logger.debug('Ping process pid %s finished with returncode %s', p.pid, p.returncode)
    if p.returncode != 0:
        logger.debug('Ping command pid %s stderr: %r', p.pid, stderr)
        raise Exception('Ping command finished with returncode {}'.format(p.returncode))
    report['state'].update(parse_ping_output(stdout))


def parse_ping_output(stdout):
    if isinstance(stdout, bytes):
        stdout = stdout.decode()
    lines = stdout.splitlines()
    if re.match(r'^--- .* ping statistics ---$', lines[-3]):
        m1 = (
            re.match(r'^[0-9]+ packets transmitted, [0-9]+ packets received, ([0-9.]+)% packet loss$', lines[-2]) or
            re.match(r'^[0-9]+ packets transmitted, [0-9]+ received, ([0-9.]+)% packet loss, time [0-9.]+ms$', lines[-2]))
        m2 = (
            re.match(r'^round-trip min/avg/max/stddev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms$', lines[-1]) or
            re.match(r'^rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms$', lines[-1]))

        logger.debug('m1: %r', m1)
        logger.debug('m2: %r', m2)

        if m1 and m2:
            packet_loss_pct, = m1.groups()
            rtt_min, rtt_avg, rtt_max, rtt_stddev = m2.groups()
            return {
                'packet_loss': {
                    '__value': float(packet_loss_pct),
                    '__unit': 'percents',
                    '__check': {
                        'state': check_state_from_packet_loss_pct(float(packet_loss_pct)),
                    },
                },
                'rtt': {
                    'min': rtt_ms_value(float(rtt_min)),
                    'avg': rtt_ms_value(float(rtt_avg)),
                    'max': rtt_ms_value(float(rtt_max)),
                    'stddev': float(rtt_stddev),
                },
            }

    raise Exception('Could not parse ping output: {!r}'.format(stdout))


def rtt_ms_value(ms):
    return {
        '__value': ms,
        '__unit': 'milliseconds',
        '__check': {
            'state': check_state_from_ms_rtt(ms),
        },
    }


def check_state_from_ms_rtt(ms):
    if ms < 300:
        return 'green'
    return 'red'


def check_state_from_packet_loss_pct(packet_loss_pct):
    if packet_loss_pct < 5:
        return 'green'
    elif packet_loss_pct < 10:
        return 'yellow'
    else:
        return 'red'


def generate_label(conf, target):
    label = {
        'agent': 'ping',
        'host': os.environ.get('REAL_HOST') or getfqdn(),
        'address': target.address,
    }
    for src in conf.default_label, target.label:
        for k, v in src.items():
            if not v:
                label.pop(k, None)
            else:
                label[k] = v
    return label
