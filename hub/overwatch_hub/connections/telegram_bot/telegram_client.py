from aiohttp import ClientSession
from logging import getLogger


logger = getLogger(__name__)


class TelegramClientError (Exception):
    pass


class TestWebhookError (TelegramClientError):
    pass


class TelegramAPICallError (TelegramClientError):
    pass


class TelegramClient:

    api_url_template = 'https://api.telegram.org/bot{token}/{method_name}'

    def __init__(self, token):
        self.token = token

    async def __aenter__(self):
        self._session = await ClientSession().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.__aexit__(exc_type, exc, tb)
        self._session = None

    async def _call(self, method_name, params=None):
        '''
        Call Telegram API method
        '''
        try:
            url = self.api_url_template.format(token=self.token, method_name=method_name)
            params = params or {}
            async with self._session.post(url, json=params) as r:
                res = await r.json()
        except Exception as e:
            raise TelegramAPICallError(f'POST {sanitize_tokens(url)} failed: {e!r}')
        logger.debug('Telegram API %s %s response: %s', method_name, smart_repr(params), smart_repr(res))
        return res['result']

    async def get_me(self):
        return await self._call('getMe')

    async def setup_webhook(self, webhook_url):
        '''
        webhook_url should already contain some secret token
        '''
        #await self._call('getWebhookInfo')
        await self.test_webhook(webhook_url)
        await self._call('setWebhook', {'url': webhook_url, 'allowed_updates': []})

    async def test_webhook(self, webhook_url):
        try:
            async with self._session.post(webhook_url, json={'test_webhook': True}) as r:
                rj = await r.json()
        except Exception as e:
            raise TestWebhookError(f'Failed to POST {webhook_url}: {e!r}')
        if not rj.get('test_webhook_reply'):
            raise TestWebhookError('Invalid test_webhook reply: {rj}')
