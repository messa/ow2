from aiohttp.web import RouteTableDef, Response, StreamResponse, json_response
from asyncio import CancelledError, shield, create_task, sleep
from logging import getLogger
from time import monotonic as monotime
from .util import to_compact_json

logger = getLogger(__name__)

routes = RouteTableDef()


@routes.get('/')
async def root_index(request):
    return Response(text='This is Overwatch Hub\n')


@routes.post('/report')
async def post_report(request):
    model = request.app['model']
    data = await request.json()
    await shield(create_task(_just_log_exceptions(model.save_report(data))))
    return Response(text='{"ok": true}', content_type='application/json')


async def _just_log_exceptions(coro):
    # THIS IS TEMPORARY FOR INITIAL DEVELOPMENT
    try:
        return await coro
    except Exception as e:
        logger.exception('Failed to save report: %r', e)


@routes.get('/dump-snapshots')
async def dump_snapshots(request):
    '''
    For debugging purposes only - possibility of skipping snapshots due to
    race conditions between creating objectid and finishing DB insert.
    '''
    model = request.app['model']
    stream_id = request.query.get('streamId')
    after_snapshot_id = request.query.get('afterSnapshotId')
    tail = bool(int(request.query.get('tail', 0)))
    streams = await model.streams.list_all()
    streams = {s.id: s for s in streams}
    res = StreamResponse()
    res.headers['Content-Type'] = 'text/plain'
    res.enable_chunked_encoding()
    res.enable_compression()
    await res.prepare(request)
    try:
        while True:
            t = monotime()
            snapshots = await model.stream_snapshots.dump(
                stream_id=stream_id,
                after_snapshot_id=after_snapshot_id)
            if not snapshots:
                if not tail:
                    break
                logger.debug('No snapshots dumped, sleeping')
                await sleep(1)
                continue
            logger.debug(
                'Dumped %s snapshots %s - %s in %.3f s',
                len(snapshots), snapshots[0].id, snapshots[-1].id,
                monotime() - t)
            parts = []
            for snapshot in snapshots:
                stream = streams.get(snapshot.stream_id)
                if not stream:
                    stream = await model.streams.get_by_id(snapshot.stream_id)
                assert stream.id == snapshot.stream_id
                record = {
                    'id': str(snapshot.id),
                    'date': snapshot.date.isoformat(),
                    'stream': {
                        'id': snapshot.stream_id,
                        'label': stream.label,
                    },
                    'state_json': snapshot.state_json,
                }
                line = to_compact_json(record)
                parts.append(line.encode())
                parts.append(b'\n')
                after_snapshot_id = snapshot.id
            del snapshots
            chunk = b''.join(parts)
            logger.debug('Sending %.2f kB of JSONL response chunk', len(chunk) / 1024)
            await res.write(chunk)
        await res.write_eof()
    except CancelledError as e:
        logger.debug('dump_snapshots finished: %r', e)
    except Exception as e:
        logger.exception('dump_snapshots failed: %r', e)
    return res
