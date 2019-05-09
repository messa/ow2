from asyncio import shield

from .util import get_logger


logger = get_logger(__name__)


async def send_report(session, conf, report, send_report_semaphore):
    try:
        async with send_report_semaphore:
            await shield(_send_report(session, conf, report))
    except Exception as e:
        logger.warning('Failed to send report to %s: %r', conf.report_url, e)


async def _send_report(session, conf, report):
    logger.debug('Sending report to %s', conf.report_url)
    headers = {}
    if conf.report_token:
        headers['Authorization'] = 'Bearer ' + conf.report_token
    async with session.post(conf.report_url, json=report, headers=headers) as r:
        r.raise_for_status()
        logger.debug('Report sent successfully')
