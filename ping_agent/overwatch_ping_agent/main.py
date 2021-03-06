from aiohttp import ClientSession
from argparse import ArgumentParser
from asyncio import FIRST_COMPLETED, Event, Semaphore, TimeoutError
from asyncio import sleep, wait
try:
    from asyncio import all_tasks, current_task
except ImportError:
    all_tasks = current_task = None
from os import environ
from signal import SIGINT, SIGTERM
import sys

from .configuration import Configuration
from .target_check import check_target
from .util import get_logger, create_task, get_running_loop, run, AsyncExitStack


logger = get_logger(__name__)


def ping_agent_main():
    p = ArgumentParser()
    p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--conf', help='path to configuration file')
    args = p.parse_args()
    setup_logging(verbose=args.verbose)
    cfg_path = (
        args.conf or
        environ.get('OVERWATCH_PING_AGENT_CONF') or
        environ.get('CONF'))
    try:
        conf = Configuration(cfg_path)
        if not conf.targets:
            raise Exception('No targets configured')
    except Exception as e:
        logger.exception('Failed to load configuration from %s: %r', cfg_path, e)
        sys.exit('ERROR - failed to load configuration from {cfg_path}: {e!r}')
    try:
        #setup_log_file(conf.log.file_path)
        logger.debug('Ping agent starting')
        run(async_main(conf))
        logger.info('Ping agent has grafecully finished')
    except Exception as e:
        logger.exception('Ping agent failed: %r', e)
        sys.exit('ERROR: {!r}'.format(e))


async def async_main(conf):
    async with AsyncExitStack() as stack:
        session = await stack.enter_async_context(ClientSession())
        stop_event = Event()
        get_running_loop().add_signal_handler(SIGINT, stop_event.set)
        get_running_loop().add_signal_handler(SIGTERM, stop_event.set)
        send_report_semaphore = Semaphore(2)
        check_tasks = []
        try:
            # create asyncio task for each configured check target
            for target in conf.targets:
                check_tasks.append(create_task(check_target(session, conf, target, send_report_semaphore)))
                await sleep(.1)
            # all set up and (hopefully) running, now just periodically check
            logger.debug('wait start')
            stop_wait = create_task(stop_event.wait())
            done, pending = await wait(check_tasks + [stop_wait], return_when=FIRST_COMPLETED)
            #logger.debug('wait done\ndone: %r\npending: %r', done, pending)
            if not stop_event.is_set():
                logger.debug('Some task(s) unexpectedly finished: %r', done)
            for t in pending:
                logger.debug('Cancelling %r', t)
                t.cancel()
            await wait(pending)
            if not stop_event.is_set():
                raise sys.exit('Some task(s) unexpectedly finished: {!r}'.format(done))
        finally:
            if all_tasks is not None:
                logger.debug('Cleanup...')
                remaining_tasks = [t for t in all_tasks() if t is not current_task()]
                if remaining_tasks:
                    await sleep(0.1)
                    for t in remaining_tasks:
                        logger.debug('Cancelling %r', t)
                        t.cancel()
                    await wait(remaining_tasks)


def setup_logging(verbose):
    from logging import DEBUG, WARNING, StreamHandler, basicConfig, getLogger
    from .util.logging import CustomFormatter
    getLogger().setLevel(DEBUG)
    h = StreamHandler()
    h.setLevel(DEBUG if verbose else WARNING)
    h.setFormatter(CustomFormatter(strip_name_prefix=__name__.split('.')[0]))
    getLogger().addHandler(h)
