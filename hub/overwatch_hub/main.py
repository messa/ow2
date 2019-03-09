from aiohttp import web
from argparse import ArgumentParser
import asyncio
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorClient
from os import environ
import sys

from .configuration import Configuration
from .util import get_mongo_db_name
from .views import routes


logger = getLogger(__name__)


def hub_main():
    p = ArgumentParser()
    p.add_argument('--conf', '-f', help='path to configuration file')
    args = p.parse_args()
    cfg_path = args.conf or environ.get('CONF_PATH')
    if not cfg_path:
        sys.exit('ERROR: Please provide path to the configuration file.')
    try:
        conf = Configuration(cfg_path)
    except Exception as e:
        sys.exit(f'ERROR - Failed to load configuration: {e}')
    setup_logging()
    logger.info('Starting Overwatch Hub')
    try:
        asyncio.run(async_main(conf))
        logger.info('Overwatch Hub has grafecully finished')
    except BaseException as e:
        logger.exception('Overwatch Hub has failed: %r', e)
        sys.exit(f'ERROR: {e!r}')


def setup_logging():
    from logging import DEBUG, basicConfig
    basicConfig(
        format='%(asctime)s %(name)-20s %(levelname)5s: %(message)s',
        level=DEBUG)
    # TODO: datetime UTC + non-locale formatting


async def async_main(conf):
    mongo_client = AsyncIOMotorClient(conf.mongodb.uri)
    mongo_db_name = get_mongo_db_name(conf.mongodb.uri)
    mongo_db = mongo_client[mongo_db_name]
    logger.debug('db: %s', mongo_db)

    app = get_app()
    app['db'] = mongo_db
    from aiohttp.web import _run_app
    await _run_app(app)


def get_app():
    app = web.Application()
    app.router.add_routes(routes)
    return app
