from aiohttp import web
from aiohttp_graphql import GraphQLView
from argparse import ArgumentParser
import asyncio
from contextlib import AsyncExitStack
from graphql.execution.executors.asyncio import AsyncioExecutor as GQLAIOExecutor
from logging import getLogger
from os import environ
import sys

from .configuration import Configuration
from .connections import AlertWebhooks
from .views import routes
from .model import get_model
from .graphql import graphql_schema


logger = getLogger(__name__)


def hub_main():
    p = ArgumentParser()
    p.add_argument('--version', action='version', version='2.0.0')
    # TODO: put the version in a single location (it's also in setup.py)
    p.add_argument('--conf', '-f', help='path to configuration file')
    args = p.parse_args()
    setup_logging()
    cfg_path = args.conf or environ.get('OVERWATCH_HUB_CONF') or environ.get('OW_HUB_CONF')
    if not cfg_path:
        sys.exit('ERROR: Please provide path to the configuration file.')
    try:
        conf = Configuration(cfg_path)
    except Exception as e:
        sys.exit(f'ERROR - Failed to load configuration from {cfg_path}: {e}')
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
    async with AsyncExitStack() as stack:
        alert_webhooks = await stack.enter_async_context(AlertWebhooks(conf.alert_webhooks))
        model = await stack.enter_async_context(get_model(conf, alert_webhooks=alert_webhooks))
        alert_webhooks.set_model(model)
        app = web.Application()
        app['model'] = model
        app.router.add_routes(routes)
        GraphQLView.attach(
                app,
                route_path='/graphql',
                schema=graphql_schema,
                graphiql=True,
                enable_async=True,
                executor=GQLAIOExecutor())
        from aiohttp.web import _run_app
        # ^^^ https://github.com/aio-libs/aiohttp/blob/baddbfe182a5731d5963438f317cbcce4c094f39/aiohttp/web.py#L261
        logger.debug('Listening on http://localhost:%s', conf.port)
        await _run_app(app, port=conf.port)
