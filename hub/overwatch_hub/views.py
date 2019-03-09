from aiohttp.web import RouteTableDef, Response
from asyncio import shield, create_task
from bson import ObjectId
from logging import getLogger


logger = getLogger(__name__)

routes = RouteTableDef()


@routes.get('/')
async def root_index(request):
    return Response(text='This is Overwatch Hub\n')


@routes.post('/report')
async def post_report(request):
    data_text = await request.text()
    await shield(create_task(save_report(request, data_text)))
    return Response(text='{"ok": true}', content_type='application/json')


async def save_report(request, data_text):
    try:
        db = request.app['db']
        del request
        doc = {'_id': ObjectId(), 'data': data_text}
        res = await db['rawReports'].insert_one(doc)
        logger.info('Inserted into rawReports: %s', res.inserted_id)
    except Exception as e:
        logger.exception('Failed to process report: %r', e)
        raise e
