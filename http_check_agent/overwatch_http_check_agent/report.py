from asyncio import shield
from functools import partial

from .util import get_logger, async_retry


logger = get_logger(__name__)


async def send_report(session, conf, report, send_report_semaphore):
    try:
        await async_retry(partial(_try_send_report, session, conf, report, send_report_semaphore))
    except Exception as e:
        logger.warning('Failed to send report to %s: %r', conf.report_url, e)


async def _try_send_report(session, conf, report, send_report_semaphore):
    async with send_report_semaphore:
        await shield(_send_report(session, conf, report))


async def _send_report(session, conf, report):
    logger.debug('Sending report to %s', conf.report_url)
    headers = {}
    if conf.report_token:
        headers['Authorization'] = 'Bearer ' + conf.report_token
    async with session.post(conf.report_url, json=report, headers=headers) as r:
        r.raise_for_status()
        logger.debug('Report sent successfully')
