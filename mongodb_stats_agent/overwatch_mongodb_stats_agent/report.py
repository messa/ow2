import requests

from .util import get_logger


logger = get_logger(__name__)

rs = requests.session()


def send_report(conf, report):
    try:
        _send_report(conf, report)
    except Exception as e:
        logger.warning('Failed to send report to %s: %r', conf.report_url, e)


def _send_report(conf, report):
    logger.debug('Sending report to %s', conf.report_url)
    headers = {}
    if conf.report_token:
        headers['Authorization'] = 'Bearer ' + conf.report_token
    r = rs.post(conf.report_url, json=report, headers=headers)
    r.raise_for_status()
    logger.debug('Report sent successfully')
