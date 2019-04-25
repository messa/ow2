#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from logging import getLogger
import os
from pathlib import Path
from random import random
import requests
from socket import getfqdn
import sys
from time import time


logger = getLogger('mock_alert_agent')

default_report_url = 'http://localhost:8485/report'


def main():
    p = ArgumentParser()
    p.add_argument('--url', help='Hub report URL')
    p.add_argument('--token', help='Hub report secret token')
    p.add_argument('command')
    args = p.parse_args()
    report_url = args.url or os.environ.get('REPORT_URL') or default_report_url
    report_token = args.token or os.environ.get('REPORT_TOKEN') or None
    setup_logging()
    if args.command == 'red':
        logger.info('Reporting check red')
        report(report_url, report_token, check_state='red')
    elif args.command == 'green':
        logger.info('Reporting check green')
        report(report_url, report_token, check_state='green')
    elif args.command == 'watchdog':
        report(report_url, report_token, watchdog=True)
    else:
        sys.exit('Unknown command')


def setup_logging():
    from logging import DEBUG, basicConfig
    basicConfig(
        format='%(asctime)s %(name)s %(levelname)5s: %(message)s',
        level=DEBUG)


def report(report_url, report_token, check_state=None, watchdog=None):
    payload = {
        'date': datetime.utcnow().isoformat(),
        'label': {
            'host': getfqdn(),
            'agent': 'mock_alert_agent',
        },
        'state': {
            'agent_script_path': str(Path(__file__).resolve()),
        },
    }
    if check_state:
        assert check_state in ['green', 'red']
        payload['state']['sample_check'] = {
            '__value': random() + (check_state == 'green'),
            '__check': {
                'state': check_state,
            },
        }
    if watchdog:
        payload['state']['sample_watchdog'] = {
            '__watchdog': {
                'deadline': int((time() + 3) * 1000),
            },
        }
    headers = {}
    if report_token:
        headers['Authorization'] = 'Bearer ' + report_token
    r = requests.post(report_url, headers=headers, json=payload)
    r.raise_for_status()
    print(r.json())


if __name__ == '__main__':
    main()
