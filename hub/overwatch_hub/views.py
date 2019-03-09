from aiohttp.web import RouteTableDef, Response


routes = RouteTableDef()


@routes.get('/')
async def root_index(request):
    return Response(text='This is Overwatch Hub')
