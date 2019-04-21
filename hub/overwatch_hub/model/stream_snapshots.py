from asyncio import shield
from bson import ObjectId
from collections import namedtuple
from datetime import datetime
from logging import getLogger
from pymongo import ASCENDING as ASC
from pymongo import DESCENDING as DESC
from pytz import utc

from ..util import to_compact_json
from .helpers import to_objectid, parse_state, flatten_state_items_tree


logger = getLogger(__name__)


def to_utc(dt):
    return utc.normalize(dt) if dt.tzinfo else utc.localize(dt)


class StreamSnapshots:

    def __init__(self, db):
        self._c_snapshots = db['streams.snapshots']
        self._c_states = db['streams.snapshots.states']

    def _stream_snapshot(self, **kwargs):
        return StreamSnapshot(c_states=self._c_states, **kwargs)

    async def create_optional_indexes(self):
        await self._c_snapshots.create_index([
            ('stream_id', ASC),
            ('date', DESC),
        ])

    async def insert(self, date, stream_id, state):
        assert isinstance(date, datetime)
        assert isinstance(stream_id, str)
        assert isinstance(state, dict)
        doc_snapshot = {
            '_id': ObjectId(),
            'stream_id': stream_id,
            'date': date,
        }
        doc_state = {
            '_id': doc_snapshot['_id'],
            'state_json': to_compact_json(state),
        }
        await self._c_states.insert_one(doc_state)
        await self._c_snapshots.insert_one(doc_snapshot)
        logger.info('Inserted %s %s', self._c_snapshots.name, doc_snapshot['_id'])
        return self._stream_snapshot(doc_snapshot=doc_snapshot, doc_state=doc_state)

    async def get_latest(self, stream_id):
        assert isinstance(stream_id, str)
        doc = await self._c_snapshots.find_one(
            {'stream_id': stream_id},
            sort=[('date', DESC)])
        return self._stream_snapshot(doc_snapshot=doc)

    async def get_by_id(self, snapshot_id):
        assert isinstance(snapshot_id, str)
        doc = await self._c_snapshots.find_one({'_id': to_objectid(snapshot_id)})
        return self._stream_snapshot(doc_snapshot=doc)

    async def get_by_ids(self, snapshot_ids, load_state=True):
        snapshot_ids = [to_objectid(x) for x in snapshot_ids]
        q = {'_id': {'$in': snapshot_ids}}
        docs = await self._c_snapshots.find(q).to_list(length=None)
        docs = {doc['_id']: doc for doc in docs}
        state_docs = {}
        if load_state:
            state_docs = await self._c_states.find(q).to_list(length=None)
            state_docs = {doc['_id']: doc for doc in state_docs}
        return [
            self._stream_snapshot(
                doc_snapshot=docs[snapshot_id],
                doc_state=state_docs.get(snapshot_id))
            for snapshot_id in snapshot_ids]

    async def list_by_stream_id(self, stream_id):
        assert isinstance(stream_id, str)
        c = self._c_snapshots.find(
            {'stream_id': stream_id},
            sort=[('date', DESC)],
            limit=10000)
        docs = await c.to_list(length=None)
        return [self._stream_snapshot(doc_snapshot=doc) for doc in docs]

    async def dump(self, stream_id=None, after_snapshot_id=None):
        q = {}
        if stream_id:
            assert isinstance(stream_id, str)
            q['stream_id'] = stream_id
        if after_snapshot_id:
            q['_id'] = {'$gt': to_objectid(after_snapshot_id)}
        c = self._c_snapshots.find(q, sort=[('_id', ASC)], limit=500)
        snapshot_docs = await shield(c.to_list(length=None))
        state_q = {'_id': {'$in': [d['_id'] for d in snapshot_docs]}}
        state_docs = await shield(self._c_states.find(state_q).to_list(length=None))
        state_docs = {d['_id']: d for d in state_docs}
        out = []
        for snapshot_doc in snapshot_docs:
            doc_state = state_docs.get(snapshot_doc['_id'])
            if not doc_state and not snapshot_doc['state_json']:
                logger.info('%s id %s not found', self._c_states.name, snapshot_doc['_id'])
                continue
            out.append(self._stream_snapshot(
                doc_snapshot=snapshot_doc,
                doc_state=doc_state,
            ))
        return out


# class StreamSnapshotMetadata:
#
#     __slots__ = ('id', 'date', 'stream_id')
#
#     def __init__(self, doc_snapshot):
#         self.id = doc_snapshot['_id']
#         self.date = to_utc(doc_snapshot['date'])
#         self.stream_id = doc_snapshot['stream_id']
#
#     def __repr__(self):
#         return f'<{self.__class__.__name__} {self.id}>'


class StreamSnapshot:

    __slots__ = (
        'id', 'date', 'stream_id',
        '_c_states', '_state_json',
        '_raw_state_items_tree', '_raw_state_items', '_state_items',
    )

    def __init__(self, c_states, doc_snapshot, doc_state=None):
        assert not doc_state or doc_snapshot['_id'] == doc_state['_id']
        self._c_states = c_states
        self.id = doc_snapshot['_id']
        self.date = to_utc(doc_snapshot['date'])
        self.stream_id = doc_snapshot['stream_id']
        if doc_snapshot.get('state_json'):
            self._state_json = doc_snapshot.get('state_json')
        elif doc_state:
            self._state_json = doc_state['state_json']
        else:
            self._state_json = None
        self._raw_state_items_tree = None
        self._raw_state_items = None
        self._state_items = None

    async def load_state(self):
        if self._state_json is not None:
            return
        assert isinstance(self.id, ObjectId)
        doc = await self._c_states.find_one({'_id': self.id})
        self._state_json = doc['state_json']

    @property
    def state_json(self):
        if self._state_json is None:
            raise Exception('state_json is not loaded')
        return self._state_json

    @property
    def raw_state_items_tree(self):
        if self._raw_state_items_tree is None:
            self._raw_state_items_tree = parse_state(self.state_json)
        return self._raw_state_items_tree

    @property
    def raw_state_items(self):
        if self._raw_state_items is None:
            self._raw_state_items = flatten_state_items_tree(self.raw_state_items_tree)
        return self._raw_state_items

    @property
    def state_items(self):
        if self._state_items is None:
            self._state_items = [
                snapshot_item_from_raw(
                    raw_item,
                    snapshot_id=self.id,
                    stream_id=self.stream_id)
                for raw_item in self.raw_state_items
            ]
        return self._state_items

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'


def snapshot_item_from_raw(raw_item, snapshot_id, stream_id):
    assert isinstance(raw_item, dict)
    assert isinstance(snapshot_id, ObjectId)
    assert raw_item['key'] == raw_item['path'][-1]
    return SnapshotItem(
        path=raw_item['path'],
        value=raw_item['value'],
        unit=raw_item.get('unit'),
        raw_counter=raw_item.get('counter'),
        raw_check=raw_item.get('check'),
        raw_watchdog=raw_item.get('watchdog'),
        snapshot_id=snapshot_id,
        stream_id=stream_id,
    )


SnapshotItemBase = namedtuple('SnapshotItemBase', '''
    path value unit raw_counter raw_check raw_watchdog
    snapshot_id stream_id
''')


class SnapshotItem (SnapshotItemBase):

    __slots__ = ()

    @property
    def key(self):
        return self.path[-1]

    @property
    def is_counter(self):
        return bool(self.raw_counter)

    @property
    def path_str(self):
        return ' > '.join(self.path)
