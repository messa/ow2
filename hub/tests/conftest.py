import os
from pathlib import Path
from pytest import fixture


here = Path(__file__).resolve().parent

on_CI = bool(os.environ.get('CI'))

default_db_uri = 'mongodb://127.0.0.1:27017/test_ow2_hub'

mongo_client_options = dict(
    maxIdleTimeMS=6 * 1000,
    socketTimeoutMS=1 * 1000,
    connectTimeoutMS=3 * 1000,
    serverSelectionTimeoutMS=1 * 1000,
    waitQueueTimeoutMS=1 * 1000,
    appname='ow2-hub-tests',
    retryWrites=True,
)


basicConfig(
    format='%(name)s %(levelname)5s: %(message)s',
    level=DEBUG)


@fixture
def db_uri():
    return os.environ.get('TEST_MONGO_URI') or default_db_uri


@fixture
async def db_client(db_uri):
    from motor.motor_asyncio import AsyncIOMotorClient
    mc_kwargs = dict(mongo_client_options)
    return AsyncIOMotorClient(db_uri, **mc_kwargs)


@fixture
async def db(db_client, db_uri):
    from overwatch_hub.util import get_mongo_db_name
    db_name = get_mongo_db_name(db_uri)
    await db_client.drop_database(db_name)
    return db_client[db_name]


@fixture
async def model(db):
    from overwatch_hub.model import Model
    async with Model(db=db, create_optional_indexes=False) as model:
        yield model
