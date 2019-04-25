from bson import ObjectId
from pytz import utc
from simplejson import loads as json_loads


def to_utc(dt):
    return utc.normalize(dt) if dt.tzinfo else utc.localize(dt)


def to_objectid(v):
    try:
        return v if isinstance(v, ObjectId) else ObjectId(v)
    except Exception as e:
        raise Exception(f'Cannot convert {v!r} to ObjectId: {e!r}')


def parse_state(state):
    if isinstance(state, str):
        state = json_loads(state)
    items = []
    assert isinstance(state, dict)
    for k, v in state.items():
        if isinstance(v, dict):
            is_meta_obj = '__value' in v or '__check' in v or '__watchdog' in v
            if is_meta_obj:
                items.append({
                    'key': k,
                    'value': v.get('__value'),
                    'unit': v.get('__unit'),
                    'counter': v.get('__counter'),
                    'check': v.get('__check'),
                    'watchdog': v.get('__watchdog'),
                })
            else:
                items.append({
                    'key': k,
                    'items': parse_state(v),
                })
        else:
            items.append({
                'key': k,
                'value': v,
            })
    return items


def flatten_state_items_tree(nested_items):
    flat_items = []
    _flatten(flat_items, nested_items, ())
    return flat_items


def _flatten(flat_items, nested_items, path):
    for item in nested_items:
        item = dict(item)
        item['path'] = path + (item['key'], )
        if item.get('value') is not None or item.get('check') or item.get('watchdog'):
            flat_items.append(item)
        if 'items' in item:
            _flatten(flat_items, item.pop('items'), item['path'])
