import asyncio
from asyncio import CancelledError
from datetime import datetime
from inspect import isawaitable
from logging import getLogger
from time import monotonic as monotime
from weakref import proxy as weakproxy

from ..util import to_utc


logger = getLogger(__name__)

DEBUG = False


class WatchdogChecker:

    def __init__(self, model):
        self._model = weakproxy(model)
        self._scheduler = Scheduler()

    def stop(self):
        self._scheduler.stop()

    async def check_all_streams(self):
        logger.debug('check_all_streams start')
        t = monotime()
        streams = await self._model.streams.list_all()
        tasks = []
        for stream in streams:
            tasks.append(asyncio.create_task(self.check_stream(stream_id=stream.id)))
        if tasks:
            await asyncio.wait(tasks)
        logger.debug('check_all_streams finished in %.3f s', monotime() - t)

    async def check_stream(self, stream_id, snapshot=None):
        '''
        Returns datetime of the nearest watchdog deadline check, or None
        '''
        try:
            logger.debug('check_stream %s', stream_id)
            deadlines = []
            if not snapshot:
                snapshot = await self._model.stream_snapshots.get_latest(stream_id=stream_id)
            await snapshot.load_state()
            now = to_utc(datetime.utcnow())
            for item in snapshot.state_items:
                if item.watchdog_deadline is None:
                    continue
                if item.watchdog_deadline <= now:
                    await self._model.alerts.create_or_update_alert(
                        stream_id=stream_id,
                        alert_type='watchdog',
                        item_path=item.path,
                        snapshot_id=snapshot.id,
                        snapshot_date=snapshot.date,
                        item_value=item.value,
                        item_unit=item.unit)
                else:
                    assert isinstance(item.watchdog_deadline, datetime)
                    deadlines.append(item.watchdog_deadline)
            if deadlines:
                nearest_deadline = min(deadlines)
                self._scheduler.schedule(
                    key=stream_id,
                    at=nearest_deadline,
                    action=lambda: self.check_stream(stream_id))
        except Exception as e:
            logger.exception('check_stream(%r) failed: %r', stream_id, e)


class Scheduler:

    def __init__(self):
        self.tasks = {} # key -> (at date, action)

    def stop(self):
        if DEBUG:
            logger.debug('Scheduler stop')
        try:
            for at, task in self.tasks.values():
                try:
                    task.cancel()
                except Exception as e:
                    logger.debug('Failed to cancel task %r: %r', task, e)
        finally:
            self.tasks.clear()

    def schedule(self, key, at, action):
        assert isinstance(at, datetime)
        if key in self.tasks:
            current_at, current_task = self.tasks[key]
            if current_at == at:
                if not current_task.cancelled() and not current_task.done():
                    if DEBUG:
                        logger.debug('Not scheduling %s at %s - already scheduled at %s')
                    return
            del self.tasks[key]
            try:
                current_task.cancel()
            except Exception as e:
                logger.debug('Failed to cancel task %r: %r', current_task, e)
        task = asyncio.create_task(self._task(key, at, action))
        self.tasks[key] = (at, task)
        if DEBUG:
            logger.debug('Scheduled key %s at %s', key, at)

    async def _task(self, key, at, action):
        delta = at - to_utc(datetime.utcnow())
        delta_s = delta.total_seconds()
        if DEBUG:
            logger.debug('Scheduled key %s at %s starting sleep %.3f s', key, at, delta_s)
        try:
            if delta_s > 0:
                await asyncio.sleep(delta_s)
        except CancelledError as e:
            if DEBUG:
                logger.debug('Scheduled key %s at %s cancelled', key, at)
            return
        if key in self.tasks:
            if self.tasks[key][0] == at:
                del self.tasks[key]
                if DEBUG:
                    logger.debug('Scheduled key %s at %s running action', key, at)
        r = action()
        if isawaitable(r):
            await r
