from bson import ObjectId
from logging import getLogger
from simplejson import dumps as json_dumps

from ..util import get_mongo_db_name, smart_repr


logger = getLogger(__name__)


mongo_client_options = dict(
    maxIdleTimeMS=60 * 1000,
    socketTimeoutMS=15 * 1000,
    connectTimeoutMS=5 * 1000,
    serverSelectionTimeoutMS=15 * 1000,
    waitQueueTimeoutMS=10 * 1000,
    appname='ow2-hub',
    retryWrites=True,
)


def get_mongo_db(mongo_conf):
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(mongo_conf.uri, **mongo_client_options)
    db_name = get_mongo_db_name(mongo_conf.uri)
    db = client[db_name]
    logger.debug('db: %s', db)
    return db


class Model:

    def __init__(self, conf):
        self.db = get_mongo_db(conf.mongodb)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.db.client.close()
        self.db = None

    async def save_report(self, report_data):
        logger.debug('save_report report_data: %s', smart_repr(report_data))
        doc = {'_id': ObjectId(), 'data': to_compact_json(report_data)}
        res = await self.db['rawReports'].insert_one(doc)
        logger.info('Inserted into rawReports: %s', res.inserted_id)


def to_compact_json(obj):
    return json_dumps(obj, separators=(',', ':'))
