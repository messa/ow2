from bson import ObjectId
from contextlib import asynccontextmanager
from logging import getLogger

from ..util import get_mongo_db_name, smart_repr, parse_datetime, to_compact_json
from .streams import Streams
from .stream_snapshots import StreamSnapshots


logger = getLogger(__name__)


mongo_client_options = dict(
    maxIdleTimeMS=60 * 1000,
    socketTimeoutMS=10 * 1000,
    connectTimeoutMS=3 * 1000,
    serverSelectionTimeoutMS=10 * 1000,
    waitQueueTimeoutMS=10 * 1000,
    appname='ow2-hub',
    retryWrites=True,
)


def get_mongo_db(mongo_conf):
    from motor.motor_asyncio import AsyncIOMotorClient
    mc_kwargs = dict(mongo_client_options)
    if mongo_conf.ssl_ca_cert_file:
        if not mongo_conf.ssl_ca_cert_file.is_file():
            raise Exception(f'ssl_ca_cert_file is not a file: {mongo_conf.ssl_ca_cert_file}')
        mc_kwargs['ssl_ca_certs'] = str(mongo_conf.ssl_ca_cert_file)
    client = AsyncIOMotorClient(mongo_conf.uri, **mc_kwargs)
    db_name = get_mongo_db_name(mongo_conf.uri)
    db = client[db_name]
    logger.debug('db: %s', db)
    return db


@asynccontextmanager
async def get_model(conf):
    db = get_mongo_db(conf.mongodb)
    try:
        async with Model(db) as model:
            yield model
    finally:
        db.client.close()


class Model:

    def __init__(self, db, create_optional_indexes=True):
        self.db = db
        self._create_optional_indexes = create_optional_indexes
        self.streams = Streams(db)
        self.stream_snapshots = StreamSnapshots(db)

    async def __aenter__(self):
        await self.create_mandatory_indexes()
        if self._create_optional_indexes:
            await self.create_optional_indexes()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.db = None

    async def create_mandatory_indexes(self):
        await self.streams.create_mandatory_indexes()

    async def create_optional_indexes(self):
        await self.stream_snapshots.create_optional_indexes()

    async def save_report(self, report_data):
        logger.debug('save_report report_data: %s', smart_repr(report_data))
        doc = {'_id': ObjectId(), 'data': to_compact_json(report_data)}
        await self.db['rawReports'].insert_one(doc)
        logger.info('Inserted rawReports %s', doc['_id'])
        report_date = parse_datetime(report_data['date'])
        report_label = report_data['label']
        report_state = report_data['state']
        unknown_keys = sorted(report_data.keys() - {'date', 'label', 'state'})
        if unknown_keys:
            logger.info('Unknown keys in report data: %s', ', '.join(unknown_keys))
        stream_id = await self.streams.resolve_id_by_label(report_label)
        await self.stream_snapshots.insert(
            date=report_date,
            stream_id=stream_id,
            state=report_state)
