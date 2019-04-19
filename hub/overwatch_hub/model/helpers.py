from bson import ObjectId
from simplejson import loads as json_loads


def to_objectid(v):
    return v if isinstance(v, ObjectId) else ObjectId(v)


def parse_state(state):
    if isinstance(state, str):
        state = json_loads(state)
    items = []
    assert isinstance(state, dict)
    for k, v in state.items():
        if isinstance(v, dict):
            is_value_obj = '__value' in v or '__check' in v or '__watchdog' in v
            if is_value_obj:
                items.append({
                    'key': k,
                    'value': v.get('__value'),
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


def flatten_nested_state_items(nested_items):
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
