from aiohttp import web
from argparse import ArgumentParser
import asyncio
from logging import getLogger
from os import environ
import sys

from .configuration import Configuration
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
        asyncio.run(async_main())
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


async def async_main():
    app = get_app()
    from aiohttp.web import _run_app
    await _run_app(app)



def get_app():
    app = web.Application()
    app.router.add_routes(routes)
    return app
