from overwatch_hub.util import utc_datetime_from_ms_timestamp
from overwatch_hub.util import LRUCache
from overwatch_hub.util import sanitize_tokens


def test_utc_datetime_from_ms_timestamp():
    assert utc_datetime_from_ms_timestamp(1556214726315).isoformat() == '2019-04-25T17:52:06.315000+00:00'


def test_lru_cache_get_set():
    c = LRUCache()
    c.set('foo', 'bar')
    assert c.get('foo') == 'bar'


def test_sanitize_tokens():
    assert sanitize_tokens('') == ''
    assert sanitize_tokens('foobar') == 'foobar'
    assert sanitize_tokens('foo1234567890bar') == 'foo..bar'
    assert sanitize_tokens('https://user:foo1234567890bar@example.com/') == 'https://user:foo..bar@example.com/'