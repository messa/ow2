from aiohttp import ClientSession
from argparse import ArgumentParser
import asyncio
from contextlib import AsyncExitStack
from logging import getLogger
from os import environ


logger = getLogger(__name__)


def http_check_agent_main():
    p = ArgumentParser()
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--conf', help='path to configuration file')
    args = p.parse_args()
    setup_logging(verbose=args.verbose)
    cfg_path = args.conf or environ.get('OVERWATCH_HTTP_CHECK_AGENT_CONF') or environ.get('CONF')
    conf = Configuration(cfg_path)
    asyncio.run(async_main())


async def async_main():
    async with AsyncExitStack() as stack:
        session = stack.enter_async_context(ClientSession())


def setup_logging(verbose):
    from logging import DEBUG, WARNING, Formatter, StreamHandler, basicConfig, getLogger
    log_format = '%(asctime)s %(name)-30s %(levelname)5s: %(message)s'
    getLogger().setLevel(DEBUG)
    h = StreamHandler()
    h.setLevel(DEBUG if verbose else WARNING)
    h.setFormatter(Formatter(log_format))
    getLogger().addHandler(h)
