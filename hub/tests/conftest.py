from collections import defaultdict
from logging import DEBUG, basicConfig, getLogger
import os
from pathlib import Path
import pytest_asyncio
from pytest import fixture, skip


logger = getLogger(__name__)

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


@pytest_asyncio.fixture
async def db_client(db_uri):
    from motor.motor_asyncio import AsyncIOMotorClient
    if db_uri == 'NONE':
        skip('TEST_MONGO_URI is NONE - skipping tests depending on DB')
    mc_kwargs = dict(mongo_client_options)
    return AsyncIOMotorClient(db_uri, **mc_kwargs)


@pytest_asyncio.fixture
async def db(db_client, db_uri):
    from overwatch_hub.util import get_mongo_db_name
    db_name = get_mongo_db_name(db_uri)
    await db_client.drop_database(db_name)
    return db_client[db_name]


@pytest_asyncio.fixture
async def model(db):
    from overwatch_hub.model import Model
    async with Model(db=db, create_optional_indexes=False) as model:
        yield model


@fixture
def graphql(model):
    from graphql import graphql
    from overwatch_hub.graphql import graphql_schema

    async def run_graphql_query(query):
        getLogger(__name__).info('Running GraphQL query: %s', ' '.join(query.split()))
        context = {
            'model': model,
        }
        res = await graphql(
            graphql_schema,
            query,
            context_value=context)
        assert not res.errors
        return _ordered_dict_to_dict(res.data)

    return run_graphql_query


def _ordered_dict_to_dict(obj):
    if isinstance(obj, dict):
        return {k: _ordered_dict_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ordered_dict_to_dict(v) for v in obj]
    return obj


@fixture
def remove_ids():
    from itertools import count

    def _remove_ids(obj):
        translations = {}
        counter = defaultdict(count)

        def translate(prefix, v):
            if v not in translations:
                translations[v] = f'{prefix}{next(counter[prefix]):03d}'
            return translations[v]

        id_keys = 'streamId snapshotId alertId'.split()

        def r1(obj):
            if isinstance(obj, dict):
                res = {}
                for k, v in obj.items():
                    if k in id_keys and isinstance(v, str):
                        v = translate(k, v)
                    res[k] = r1(v)
                return res
            if isinstance(obj, list):
                return [r1(v) for v in obj]
            return obj

        obj = r1(obj)

        def r2(obj):
            if isinstance(obj, dict):
                res = {}
                for k, v in obj.items():
                    if isinstance(v, str) and v in translations:
                        v = translations[v]
                    res[k] = r2(v)
                return res
            if isinstance(obj, list):
                return [r2(v) for v in obj]
            return obj

        obj = r2(obj)

        return obj

    return _remove_ids
