from collections import deque
from logging import getLogger
from itertools import count
from time import monotonic as monotime


DEBUG = False

_not_present = object()

logger = getLogger(__name__)


class LRUCache:

    def __init__(self, max_size=1000, ttl_ms=60 * 1000):
        self.data = {}
        self.last_access = {}
        self.expire_queue = deque()
        self.access_counter = count()
        self.max_size = max_size
        self.ttl_ms = ttl_ms

    def get(self, key, default=None):
        if key not in self.data:
            if DEBUG:
                logger.debug('LRUCache miss: %r', key)
            return default
        value, mtime = self.data[key]
        if self.ttl_ms and mtime + self.ttl_ms < monotime():
            if DEBUG:
                logger.debug('LRUCache expired: %r', key)
            del self.data[key]
            del self.last_access[key]
            return default
        if DEBUG:
            logger.debug('LRUCache hit: %r', key)
        self._fresh(key)
        return value

    def getf(self, key, factory):
        value = self.get(key, default=_not_present)
        if value is _not_present:
            value = factory()
            self.set(key, value)
        return value

    async def agetf(self, key, factory):
        value = self.get(key, default=_not_present)
        if value is _not_present:
            value = await factory()
            self.set(key, value)
        return value

    def set(self, key, value):
        self.data[key] = (value, monotime())
        self._fresh(key)
        self._compact()

    def _fresh(self, key):
        access_number = next(self.access_counter)
        self.last_access[key] = access_number
        self.expire_queue.append((key, access_number))

    def _compact(self):
        while len(self.data) >= self.max_size:
            key, access_number = self.expire_queue.popleft()
            last = self.last_access.get(key)
            if last is None:
                assert key not in self.data
                continue
            if access_number != last:
                continue
            del self.data[key]
            del self.last_access[key]
