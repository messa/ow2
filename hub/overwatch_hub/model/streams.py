from datetime import datetime
from logging import getLogger

from ..util import random_str


logger = getLogger(__name__)


class Streams:

    def __init__(self, db):
        self._c_labels = db['streams']

    async def create_mandatory_indexes(self):
        await self._c_labels.create_index('label_str', unique=True)

    async def resolve_id_by_label(self, label):
        stream = await self.resolve_by_label(label)
        return stream.id

    async def resolve_by_label(self, label):
        assert isinstance(label, dict)
        label_str = get_label_str(label)
        try_count = 0
        while True:
            if try_count > 3:
                raise Exception(f'Too many tries: resolve_by_label({label!r})')
            try_count += 1
            doc = await self._c_labels.find_one({'label_str': label_str})
            if doc:
                return self._obj(doc)
            doc = {
                '_id': random_str(8),
                'label_str': label_str,
                'label': label,
                'created': {'date': datetime.utcnow()},
            }
            try:
                await self._c_labels.insert_one(doc)
            except Exception as e:
                logger.debug('Failed to insert %s %r: %r; trying again', self._c_labels.name, doc, e)
                continue
            logger.debug('Inserted new stream id: %r label: %r', doc['_id'], doc['label'])
            return self._obj(doc)

    def _obj(self, doc):
        return Stream(doc)

    async def get_by_id(self, stream_id):
        assert isinstance(stream_id, str)
        doc = await self._c_labels.find_one({'_id': stream_id})
        return self._obj(doc)

    async def list_all(self):
        docs = await self._c_labels.find({}).to_list(10**4)
        return [self._obj(d) for d in docs]


class Stream:

    def __init__(self, doc):
        self.id = doc['_id']
        self.label = doc['label']
        self.created_date = doc['created']['date']


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
assert get_label_str({'b': '2', 'a': '1'}) == 'a:1,b:2'
assert get_label_str({'key,:': 'value,:'}) == 'key,:::value,,:'
