from aiohttp.web import RouteTableDef, Response
from logging import getLogger


logger = getLogger(__name__)

routes = RouteTableDef()


@routes.get('/')
async def root_index(request):
    return Response(text='This is Overwatch Hub\n')


@routes.post('/report')
async def post_report(request):
    data_text = await request.text()
    db = request.app['db']
    res = await db['rawReports'].insert_one({'data': data_text})
    logger.info('Inserted into rawReports: %s', res.inserted_id)
    return Response(text='{"ok": true}', content_type='application/json')
