from aiohttp import ClientSession
from asyncio import create_task, sleep
from logging import getLogger

from ..util import smart_repr


logger = getLogger(__name__)


class AlertWebhooks:

    def __init__(self, alert_webhooks_conf, model=None):
        self._alert_webhooks_conf = alert_webhooks_conf
        self._model = model

    def set_model(self, model):
        assert self._model is None
        self._model = model

    async def __aenter__(self):
        self._session = await ClientSession().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.__aexit__(exc_type, exc, tb)
        self._session = None

    def new_alert_created(self, alert):
        logger.debug('new_alert_created')
        for conf in self._alert_webhooks_conf:
            create_task(self._send_new_alert_created(conf, alert))

    def alert_closed(self, alert):
        logger.debug('alert_closed')
        for conf in self._alert_webhooks_conf:
            create_task(self._send_alert_closed(conf, alert))

    async def _send_new_alert_created(self, webhook_conf, alert):
        logger.debug('_send_new_alert_created %s', webhook_conf)
        try_count = 0
        while True:
            if try_count > 5:
                raise Exception('Too many tries')
            if try_count > 0:
                await sleep(2**try_count)
                logger.debug('Trying again')
            try_count += 1
            stream = await self._model.streams.get_by_id(alert.stream_id)
            if webhook_conf.format == 'text':
                payload = f'\u26A0\uFE0F New alert: {alert} stream: {stream}'.encode()
                try:
                    async with self._session.post(webhook_conf.url, data=payload) as r:
                        r_text = await r.text()
                        logger.debug('Alert webhook POST %s -> %s', webhook_conf.url, smart_repr(r_text))
                except Exception as e:
                    logger.exception('Failed to send POST: %r', e)
                    continue
            else:
                raise Exception(f'Unknown webhook conf format: {webhook_conf.format}')
            break

    async def _send_alert_closed(self, webhook_conf, alert):
        logger.debug('_send_new_alert_created %s', webhook_conf)
        try_count = 0
        while True:
            if try_count > 5:
                raise Exception('Too many tries')
            if try_count > 0:
                await sleep(2**try_count)
                logger.debug('Trying again')
            try_count += 1
            stream = await self._model.streams.get_by_id(alert.stream_id)
            if webhook_conf.format == 'text':
                payload = f'\u2705 Alert closed: {alert} stream: {stream}'.encode()
                try:
                    async with self._session.post(webhook_conf.url, data=payload) as r:
                        r_text = await r.text()
                        logger.debug('Alert webhook POST %s -> %s', webhook_conf.url, smart_repr(r_text))
                except Exception as e:
                    logger.exception('Failed to send POST: %r', e)
                    continue
            else:
                raise Exception(f'Unknown webhook conf format: {webhook_conf.format}')
            break
