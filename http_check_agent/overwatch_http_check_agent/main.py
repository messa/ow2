from aiohttp import ClientSession
from argparse import ArgumentParser
import asyncio
from contextlib import AsyncExitStack
from logging import getLogger
from os import environ
from signal import SIGINT, SIGTERM
import sys

from .configuration import Configuration


logger = getLogger(__name__)


def http_check_agent_main():
    p = ArgumentParser()
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--conf', help='path to configuration file')
    args = p.parse_args()
    setup_logging(verbose=args.verbose)
    cfg_path = (
        args.conf or
        environ.get('OVERWATCH_HTTP_CHECK_AGENT_CONF') or
        environ.get('CONF'))
    try:
        conf = Configuration(cfg_path)
    except Exception as e:
        logger.exception('Failed to load configuration from %s: %r', cfg_path, e)
        sys.exit(f'ERROR - failed to load configuration from {cfg_path}: {e!r}')
    try:
        #setup_log_file(conf.log.file_path)
        logger.debug('HTTP check agent starting')
        asyncio.run(async_main(conf))
        logger.info('HTTP check agent has grafecully finished')
    except BaseException as e:
        logger.exception('HTTP check agent failed: %r', e)
        sys.exit('ERROR: {!r}'.format(e))


async def async_main(conf):
    async with AsyncExitStack() as stack:
        session = await stack.enter_async_context(ClientSession())
        stop_event = asyncio.Event()
        asyncio.get_running_loop().add_signal_handler(SIGINT, stop_event.set)
        asyncio.get_running_loop().add_signal_handler(SIGTERM, stop_event.set)
        await stop_event.wait()
        logger.debug('Cleanup...')


def setup_logging(verbose):
    from logging import DEBUG, WARNING, Formatter, StreamHandler, basicConfig, getLogger
    log_format = '%(asctime)s %(name)-31s %(levelname)5s: %(message)s'
    getLogger().setLevel(DEBUG)
    h = StreamHandler()
    h.setLevel(DEBUG if verbose else WARNING)
    h.setFormatter(Formatter(log_format))
    getLogger().addHandler(h)
