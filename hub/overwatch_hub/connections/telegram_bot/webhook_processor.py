from asyncio import create_task
from logging import getLogger
from time import time


logger = getLogger(__name__)


class WebhookProcessor:

    def __init__(self, telegram_client):
        self.telegram_client = telegram_client

    async def process_webhook(self, post_data):
        try:
            if post_data.get('test_webhook'):
                return {'test_webhook_reply': post_data['test_webhook']}
            if abs(time() - post_data['message']['date']) > 10:
                logger.info(
                    'Discarding update - too old: date %r (%s s ago)',
                    post_data['message']['date'],
                    time() - post_data['message']['date'])
            chat_id = update['message']['chat']['id']
            if update['message']['text'] == '/start':
                create_task(self.process_start(chat_id))
                return {}
        except Exception as e:
            raise Exception(f'Failed to process Telegram webhook: {e!r}; post_data: {post_data!r}')

    async def process_start(self, chat_id):
        self.telegram_client

