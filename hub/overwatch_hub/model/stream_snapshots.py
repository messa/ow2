from bson import ObjectId
from datetime import datetime
from logging import getLogger
from pymongo import ASCENDING as ASC

from ..util import to_compact_json


logger = getLogger(__name__)


class StreamSnapshots:

    def __init__(self, db):
        self._c_snapshots = db['streams.snapshots']

    async def create_optional_indexes(self):
        await self._c_snapshots.create_index([
            ('stream_id', ASC),
            ('date', ASC),
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
