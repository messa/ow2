from bson import ObjectId
from datetime import datetime
from logging import getLogger
from pymongo import ASCENDING as ASC
from pymongo import DESCENDING as DESC
from pytz import utc

from ..util import to_compact_json


logger = getLogger(__name__)


class StreamSnapshots:

    def __init__(self, db):
        self._c_snapshots = db['streams.snapshots']

    async def create_optional_indexes(self):
        await self._c_snapshots.create_index([
            ('stream_id', ASC),
            ('date', DESC),
        ])

    async def insert(self, date, stream_id, state):
        assert isinstance(date, datetime)
        assert isinstance(state, dict)
        doc = {
            '_id': ObjectId(),
            'stream_id': stream_id,
            'date': date,
            'state_json': to_compact_json(state),
        }
        await self._c_snapshots.insert_one(doc)
        logger.info('Inserted %s %s', self._c_snapshots.name, doc['_id'])

    async def get_latest(self, stream_id):
        assert isinstance(stream_id, str)
        doc = await self._c_snapshots.find_one(
            {'stream_id': stream_id},
            sort=[('date', DESC)])
        return self._obj(doc)

    def _obj(self, doc):
        return StreamSnapshot(doc)


class StreamSnapshot:

    __slots__ = ('id', 'date', 'state_json', 'stream_id')

    def __init__(self, doc):
        self.id = doc['_id']
        self.date = utc.localize(doc['date'])
        self.state_json = doc['state_json']
        self.stream_id = doc['stream_id']
