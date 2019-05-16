from overwatch_hub.util import utc_datetime_from_ms_timestamp
from overwatch_hub.util import LRUCache


def test_utc_datetime_from_ms_timestamp():
    assert utc_datetime_from_ms_timestamp(1556214726315).isoformat() == '2019-04-25T17:52:06.315000+00:00'


def test_lru_cache_get_set():
    c = LRUCache()
    c.set('foo', 'bar')
    assert c.get('foo') == 'bar'
