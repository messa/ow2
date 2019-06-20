from .sent_messages import SentMessages


class TelegramBotModel:

    def __init__(self, db):
        prefixed_db = db['telegramBot']
        self.sent_messages = SentMessages(prefixed_db)