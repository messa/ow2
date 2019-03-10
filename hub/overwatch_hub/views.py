from aiohttp.web import RouteTableDef, Response
from asyncio import shield, create_task
from logging import getLogger


logger = getLogger(__name__)

routes = RouteTableDef()


@routes.get('/')
async def root_index(request):
    return Response(text='This is Overwatch Hub\n')


@routes.post('/report')
async def post_report(request):
    data = await request.json()
    await shield(create_task(_just_log_exceptions(request.app['model'].save_report(data))))
    return Response(text='{"ok": true}', content_type='application/json')


async def _just_log_exceptions(coro):
    try:
        return await coro
    except Exception as e:
        logger.exception('Failed to save report: %r', e)
