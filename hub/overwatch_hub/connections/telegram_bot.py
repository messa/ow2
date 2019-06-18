from aiohttp import ClientSession
from asyncio import create_task
from logging import getLogger
from reprlib import repr as smart_repr
from secrets import token_hex


logger = getLogger(__name__)


class TelegramBot:

    def __init__(self, telegram_bot_conf, model=None):
        self._telegram_bot_conf = telegram_bot_conf
        self._model = model

    def set_model(self, model):
        assert self._model is None
        self._model = model

    async def __aenter__(self):
        self._client = await TelegramClient(self._telegram_bot_conf.token).__aenter__(self)
        create_task(self._setup())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)
        self._client = None

    async def _setup(self):
        me = await self._client.get_me()
        logger.debug('Telegram API me: %r', me)
        wh_url = self._public_url + '/tg-wh/update/' + self.auth_token
        logger.info('Setting up Telegram bot webhook: %s', wh_url)
        await self._client.setup_webhook()

    def new_alert_created(self, alert):
        logger.debug('new_alert_created')

    def alert_closed(self, alert):
        logger.debug('alert_closed')


class TelegramClient:

    def __init__(self, token, public_url):
        self.token = token
        self.public_url = public_url
        self.auth_token = token_hex(16)

    async def __aenter__(self):
        self._session = await ClientSession().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.__aexit__(exc_type, exc, tb)
        self._session = None

    async def _call(self, method_name, params=None):
        url = f'https://api.telegram.org/bot{self.token}/{method_name}'
        params = params or {}
        async with self._session.post(url, json=params) as r:
            res = await r.json()
            logger.debug('TG API %s %s response: %s', method_name, smart_repr(params), smart_repr(res))
            return res['result']

    async def get_me(self):
        return await self._call('getMe')

    async def setup_webhook(self, url):
        url += f'&token={self.auth_token}' if '?' in url else f'?token={self.auth_token}'
        await self._call('getWebhookInfo')
        await self._selftest()
        #logger.debug('Update webhook URL: %s', wh_url)
        await self._call('setWebhook', {'url': url, 'allowed_updates': []})
