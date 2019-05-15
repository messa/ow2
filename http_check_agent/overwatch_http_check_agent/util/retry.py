from asyncio import CancelledError, sleep
from .logging import get_logger


logger = get_logger(__name__)


async def async_retry(f, max_try_count=3):
    try_count = 0
    while True:
        try_count += 1
        if try_count > 1:
            logger.debug('Trying again (%s)', f)
        try:
            return await f()
        except CancelledError as e:
            raise e
        except Exception as e:
            if try_count >= max_try_count:
                raise e
            sleep_time = 2 ** try_count
            log = logger.info if try_count == 1 else logger.warning
            log('Failed to run %s: %r; will try again in %d s', f, e, sleep_time)
            await sleep(sleep_time)
            continue
