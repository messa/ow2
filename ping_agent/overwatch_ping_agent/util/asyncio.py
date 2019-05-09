from .logging import get_logger

logger = get_logger(__name__)

from asyncio import get_event_loop, gather

try:
    from asyncio import get_running_loop
except ImportError:
    get_running_loop = get_event_loop

try:
    from asyncio import create_task
except ImportError:
    create_task = None

try:
    from asyncio import run
except ImportError:
    run = None

try:
    from contextlib import AsyncExitStack
except ImportError:
    AsyncExitStack = None


def create_task_polyfill(coro):
    loop = get_running_loop()
    task = loop.create_task(coro)
    return task


def run_polyfill(main):
    loop = get_running_loop()
    try:
        return loop.run_until_complete(main)
    finally:
        _cancel_all_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())


def _cancel_all_tasks(loop):
    to_cancel = tasks.all_tasks(loop)
    if to_cancel:
        for task in to_cancel:
            task.cancel()
        loop.run_until_complete(gather(*to_cancel, loop=loop, return_exceptions=True))


class AsyncExitStackPolyfill:

    def __init__(self):
        self._stack = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for cm in reversed(self._stack):
            try:
                await cm.__aexit__(exc_type, exc_val, exc_tb)
            except BaseException as e:
                logger.exception('cm.__aexit__ failed: %r; cm: %r', e, cm)
        self._stack = None

    async def enter_async_context(self, cm):
        res = await cm.__aenter__()
        self._stack.append(cm)
        return res


if create_task is None:
    create_task = create_task_polyfill

if run is None:
    run = run_polyfill

if AsyncExitStack is None:
    AsyncExitStack = AsyncExitStackPolyfill
