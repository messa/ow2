from datetime import datetime, timedelta
from logging import getLogger

from ..util import random_str


logger = getLogger(__name__)


class StreamLabels:

    def __init__(self, db):
        self._c_labels = db['streams.labels']

    async def create_mandatory_indexes(self):
        await self._c_labels.create_index('label_str', unique=True)

    async def resolve_label_id(self, label):
        assert isinstance(label, dict)
        label_str = get_label_str(label)
        now = datetime.utcnow()
        doc = await self._c_labels.find_one({'label_str': label_str})
        if doc:
            if now - doc['last_used'] > timedelta(hours=1):
                await self._c_labels.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'last_used': now}})
            return doc['_id']
        doc = {
            '_id': random_str(8),
            'label_str': label_str,
            'label': label,
            'created': {'date': now},
            'last_used': now,
        }
        await self._c_labels.insert_one(doc)
        logger.debug('Inserted new stream label %r %r', doc['_id'], doc['label'])
        return doc['_id']


def get_label_str(label):
    parts = []
    for k, v in sorted(label.items()):
        if v is None:
            continue
        if parts:
            parts.append(',')
        parts.append(k.replace(':', '::'))
        parts.append(':')
        parts.append(str(v).replace(',', ',,'))
    return ''.join(parts)


assert get_label_str({'a': '1', 'b': '2'}) == 'a:1,b:2'
