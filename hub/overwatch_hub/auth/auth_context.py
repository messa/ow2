from asyncio import create_task
from logging import getLogger
from .errors import AccessDeniedError


logger = getLogger(__name__)


async def get_request_auth_context(request):
    if 'auth_context' not in request:
        request['auth_context'] = await do_get_request_auth_context(request)
    return request['auth_context']


async def do_get_request_auth_context(request):
    conf = request.app['configuration']
    model = request.app['model']
    access_token_handle = get_request_access_token_handle(request, conf)
    if access_token_handle:
        access_token = await model.access_tokens.get_by_handle(access_token_handle, default=None)
        if access_token:
            logger.debug('Access token: %r', access_token)
            await access_token.check_validity()
            create_task(access_token.update_last_used())
            return UserAuthContext(
                access_token=access_token,
                user=await model.users.get_by_id(access_token.user_id))
    return AnonymousAuthContext()


def get_request_access_token_handle(request, conf):
    if request.headers.get('Authorization'):
        try:
            ah_type, ah_token = request.headers['Authorization'].split()
        except ValueError:
            pass
        else:
            if ah_type.lower() == 'bearer':
                return ah_token
    if request.cookies.get(conf.access_token_cookie_name):
        return request.cookies[conf.access_token_cookie_name]
    return None


class AnonymousAuthContext:

    def __init__(self):
        self.access_token = None
        self.user = None

    def check_general_access(self):
        raise AccessDeniedError('Access denied (general access)')


class UserAuthContext:

    def __init__(self, access_token, user):
        self.access_token = access_token
        self.user = user

    def __repr__(self):
        return f'<{self.__class__.__name__} user={self.user!r} access_token={self.access_token!r}>'

    def check_general_access(self):
        return self
