from aiohttp.web import Application, AppRunner, TCPSite, middleware
from aiohttp_graphql import GraphQLView
from argparse import ArgumentParser
import asyncio
from contextlib import AsyncExitStack
from graphql.execution.executors.asyncio import AsyncioExecutor as GQLAIOExecutor
from logging import getLogger
from os import environ
from pymongo.errors import ConnectionFailure as MongoDBConnectionFailure
from signal import SIGINT, SIGTERM
import sys

from .auth import get_user
from .configuration import Configuration
from .connections import AlertWebhooks
from .graphql import graphql_schema
from .model import InitialConnectionError, get_model
from .views import routes


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
        # log via logging...
        log_tb = getattr(e, 'log_traceback', True)
        log = logger.exception if log_tb else logger.error
        log('Overwatch Hub has failed: %r', e)
        # ...and provide simple message (if possible) to stderr
        try:
            e_type_name = f'{type(e).__module__}.{type(e).__name__}'
        except Exception:
            e_type_name = str(type(e))
        sys.exit(f'ERROR ({e_type_name}): {e}')


def setup_logging():
    from logging import DEBUG, basicConfig
    basicConfig(
        format='%(asctime)s %(name)-20s %(levelname)5s: %(message)s',
        level=DEBUG)
    # TODO: datetime UTC + non-locale formatting


@middleware
async def auth_middleware(request, handler):
    request['get_user'] = lambda: get_user(request)
    resp = await handler(request)
    return resp


async def async_main(conf):
    async with AsyncExitStack() as stack:
        alert_webhooks = await stack.enter_async_context(AlertWebhooks(conf.alert_webhooks))
        model = await stack.enter_async_context(get_model(conf, alert_webhooks=alert_webhooks))
        alert_webhooks.set_model(model)
        app = Application(middlewares=[auth_middleware])
        app['configuration'] = conf
        app['model'] = model
        app.router.add_routes(routes)
        GraphQLView.attach(
            app,
            route_path='/graphql',
            schema=graphql_schema,
            graphiql=True,
            enable_async=True,
            executor=GQLAIOExecutor())
        runner = AppRunner(app)
        await runner.setup()
        host = conf.http_interface.bind_host
        port = conf.http_interface.bind_port
        site = TCPSite(runner, host, port)
        await site.start()
        stop_event = asyncio.Event()
        asyncio.get_running_loop().add_signal_handler(SIGINT, stop_event.set)
        asyncio.get_running_loop().add_signal_handler(SIGTERM, stop_event.set)
        logger.debug('Listening on http://%s:%s', host or 'localhost', port)
        await stop_event.wait()
        logger.debug('Cleanup...')
        t = asyncio.create_task(log_still_running_tasks())
        await runner.cleanup()
        t.cancel()
        logger.debug('Cleanup done')


async def log_still_running_tasks():
    while True:
        await asyncio.sleep(3)
        tasks = '\n'.join(f'{n:2d}. {smart_repr(t)}' for n, t in enumerate(asyncio.all_tasks(), start=1))
        logger.debug('Still running tasks:\n%s', tasks)
