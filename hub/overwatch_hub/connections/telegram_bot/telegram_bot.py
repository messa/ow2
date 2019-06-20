'''
from aiohttp.web import HTTPForbidden
from reprlib import repr as smart_repr
'''

from asyncio import create_task
from hashlib import sha256
from logging import getLogger
from secrets import compare_digest
from urllib.parse import urlencode

from .telegram_client import TelegramClient
from .webhook_processor import WebhookProcessor


logger = getLogger(__name__)


class TelegramBot:

    def __init__(self, telegram_bot_conf, model=None, telegram_client=None):
        self._telegram_token = telegram_bot_conf.token
        self._public_url = telegram_bot_conf.public_url
        self._public_url_token = get_public_url_token(self._telegram_token)
        self._model = model
        self._telegram_client = telegram_client or TelegramClient(self._telegram_token)
        self._webhook_processor = WebhookProcessor(self._telegram_client)

    def set_model(self, model):
        assert self._model is None
        self._model = model

    async def __aenter__(self):
        self._telegram_client = await self._telegram_client.__aenter__()
        create_task(self._setup())
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._telegram_client.__aexit__(exc_type, exc, tb)
        self._telegram_client = None

    async def _setup(self):
        me = await self._cli_telegram_clientent.get_me()
        logger.debug('Telegram API me: %r', me)
        webhook_url = add_query_param(self._public_url, token=self._public_url_token)
        logger.info('Setting up Telegram bot webhook: %s', webhook_url)
        await self._telegram_client.setup_webhook(webhook_url)

    async def process_webhook(self, url_query, post_data):
        authorized = compare_digest(
            url_query['token'].encode(),
            self._public_url_token.encode())
        if not authorized:
            raise HTTPForbidden(text='Invalid public URL token')
        return await self._webhook_processor.process_webhook(post_data)

    def new_alert_created(self, alert):
        logger.debug('new_alert_created')

    def alert_closed(self, alert):
        logger.debug('alert_closed')


def get_public_url_token(telegram_token):
    '''
    We need to be sure that requests going to the public_url are from Telegram.
    We can add some secret token to the URL we set as our Telegram webhook endpoint.
    What secret token we use? Something only we know - our Telegram token :)
    Let's just hash it so we don't use the Telegram token itself unnecessary.
    '''
    assert isinstance(telegram_token, str)
    return sha256(telegram_token.encode()).hexdigest()[:10]


def add_query_param(url, **params):
    if '?' in url:
        return url + '&' + urlencode(params)
    else:
        return url + '?' + urlencode(params)
