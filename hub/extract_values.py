#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime
from logging import getLogger
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from simplejson import loads as json_loads
from simplejson import dumps as json_dumps
import sys
from time import monotonic as monotime


logger = getLogger('extract_values')


def main():
    setup_logging()
    client = MongoClient()
    #db = client['dev_ow_hub']
    db = client['ow2_hub']
    streams = list(db['streams'].find())
    logger.info('Loaded %d streams', len(streams))

    db['streams.hourly.meta'].create_index([('stream_id', 1), ('date_hour', 1)], unique=True)
    db['streams.hourly.snapshotValues'].create_index([('stream_id', 1), ('date_hour', 1), ('path_json', 1)], unique=True)
    logger.info('Created indexes')

    for stream in streams:
        process_stream(db, stream)


def process_stream(db, stream):
    logger.info('Processing stream %s %s', stream['_id'], stream['label'])
    snapshots = list(db['streams.snapshots'].find({'stream_id': stream['_id']}))
    t = monotime()
    logger.debug('Loaded %d snapshots in %.3f s', len(snapshots), monotime() - t)
    if not snapshots:
        return
    by_date_hour = defaultdict(list)
    for s in snapshots:
        assert isinstance(s['date'], datetime)
        date_hour = s['date'].isoformat()[:13]
        by_date_hour[date_hour].append(s)
    date_hours = by_date_hour.keys()
    logger.debug('%d napshot date hours (%s - %s)', len(date_hours), min(date_hours), max(date_hours))
    for date_hour, dh_snapshots in sorted(by_date_hour.items()):
        logger.debug('Processing stream %s interval %s', stream['_id'], date_hour)
        snapshot_ids = [s['_id'] for s in dh_snapshots]
        t = monotime()
        states = list(db['streams.snapshots.states'].find({'_id': {'$in': snapshot_ids}}))
        logger.debug('Loaded %d states in %.3f s', len(states), monotime() - t)
        states_by_id = {s['_id']: s for s in states}

        interval_snapshot_ids = {}
        interval_dates = set()
        interval_values = defaultdict(dict)

        db['streams.hourly.meta'].delete_many({
            'stream_id': stream['_id'],
            'date_hour': date_hour,
        })
        db['streams.hourly.values'].delete_many({
            'stream_id': stream['_id'],
            'date_hour': date_hour,
        })

        for snapshot in dh_snapshots:
            state = states_by_id[snapshot['_id']]
            assert state['_id'] == snapshot['_id']
            assert snapshot['date'].isoformat().startswith(date_hour)
            interval_dates.add(snapshot['date'])
            interval_snapshot_ids[snapshot['date']] = snapshot['_id']
            state_items = flatten_state_items_tree(parse_state(state['state_json']))
            for item in state_items:
                if item.get('value') is not None:
                    interval_values[item['path']][snapshot['date']] = item['value']

        if interval_dates:
            interval_dates = sorted(interval_dates)
            meta_doc = {
                'stream_id': stream['_id'],
                'date_hour': date_hour,
                'snapshot_ids': [interval_snapshot_ids[dt] for dt in interval_dates],
                'snapshot_dates': interval_dates,
            }
            value_docs = []
            for value_path, value_instances in sorted(interval_values.items()):
                value_docs.append({
                    'stream_id': stream['_id'],
                    'date_hour': date_hour,
                    'path': value_path,
                    'path_str': ' :: '.join(value_path),
                    'path_json': to_compact_json(value_path),
                    'values': [value_instances.get(dt) for dt in interval_dates],
                })
            db['streams.hourly.meta'].insert_one(meta_doc)
            if value_docs:
                try:
                    db['streams.hourly.snapshotValues'].insert_many(value_docs)
                except BulkWriteError as e:
                    print(value_docs)
                    print(e)
                    print(dir(e))
                    print(e.code)
                    print(e.details)
                    sys.exit(repr(e))


def setup_logging():
    from logging import DEBUG, basicConfig
    basicConfig(
        format='%(asctime)s %(name)s %(levelname)5s: %(message)s',
        level=DEBUG)


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


def to_compact_json(obj):
    return json_dumps(obj, separators=(',', ':'))


if __name__ == '__main__':
    main()
