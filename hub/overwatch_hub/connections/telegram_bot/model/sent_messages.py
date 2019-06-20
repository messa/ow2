from logging import getLogger


logger = getLogger(__name__)


class SentMessages:

    def __init__(self, db):
        self._c_sent = db['sentMessages']