from asyncio import shield
from bson import ObjectId
from datetime import datetime
from logging import getLogger
from pymongo import ASCENDING as ASC
from pymongo import DESCENDING as DESC
from pytz import utc

from ..util import to_compact_json
from .helpers import to_objectid


logger = getLogger(__name__)


class StreamSnapshots:

    def __init__(self, db):
        self._c_snapshots = db['streams.snapshots']
        self._c_states = db['streams.snapshots.states']

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
        return await self._obj(doc_snapshot, doc_state)

    async def get_latest(self, stream_id):
        assert isinstance(stream_id, str)
        doc = await self._c_snapshots.find_one(
            {'stream_id': stream_id},
            sort=[('date', DESC)])
        return await self._obj(doc)

    async def get_by_id(self, snapshot_id):
        assert isinstance(snapshot_id, str)
        doc = await self._c_snapshots.find_one({'_id': to_objectid(snapshot_id)})
        return await self._obj(doc)


    async def get_latest_metadata(self, stream_id):
        assert isinstance(stream_id, str)
        doc = await self._c_snapshots.find_one(
            {'stream_id': stream_id},
            sort=[('date', DESC)])
        return StreamSnapshotMetadata(doc)

    async def list_metadata(self, stream_id):
        assert isinstance(stream_id, str)
        c = self._c_snapshots.find(
            {'stream_id': stream_id},
            sort=[('date', DESC)],
            limit=10000)
        docs = await c.to_list(length=None)
        return [StreamSnapshotMetadata(doc) for doc in docs]

    async def _obj(self, doc_snapshot, doc_state=None):
        if not doc_state and not doc_snapshot.get('state_json'):
            doc_state = await self._c_states.find_one({'_id': doc_snapshot['_id']})
        return StreamSnapshot(doc_snapshot, doc_state)

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
            out.append(StreamSnapshot(
                doc_snapshot=snapshot_doc,
                doc_state=doc_state,
            ))
        return out


class StreamSnapshotMetadata:

    __slots__ = ('id', 'date', 'stream_id')

    def __init__(self, doc_snapshot):
        self.id = doc_snapshot['_id']
        self.date = utc.localize(doc_snapshot['date'])
        self.stream_id = doc_snapshot['stream_id']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'


class StreamSnapshot:

    __slots__ = ('id', 'date', 'stream_id',  'state_json')

    def __init__(self, doc_snapshot, doc_state):
        assert not doc_state or doc_snapshot['_id'] == doc_state['_id']
        self.id = doc_snapshot['_id']
        self.date = utc.localize(doc_snapshot['date'])
        self.stream_id = doc_snapshot['stream_id']
        self.state_json = doc_snapshot.get('state_json') or doc_state['state_json']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
