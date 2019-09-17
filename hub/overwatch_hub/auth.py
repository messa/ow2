from asyncio import get_running_loop
from logging import getLogger
from urllib.parse import unquote
from requests_oauthlib import OAuth2Session


logger = getLogger(__name__)

token_cookie_name = 'ow2token'


class AuthCache:
    pass


async def get_user(request):
    if 'user' not in request:
        if 'auth_cache' not in request.app:
            request.app['auth_cache'] = AuthCache()
        request['user'] = await _get_user(request)
    return request['user']


async def _get_user(request):
    if request.cookies.get(token_cookie_name):
        return await user_from_token_cookie(request, request.cookies[token_cookie_name])
    return None


async def user_from_token_cookie(request, cookie_value):
    cookie_value = unquote(cookie_value)
    provider, token = cookie_value.split(':', 1)
    if provider == 'google':
        user = GoogleUser(request=request, access_token=token)
        await user.load()
        return user
    logger.warning('Could not parse token cookie: %r', token_cookie_value)
    return None


class GoogleUser:

    def __init__(self, request, access_token):
        self._request = request
        self._access_token = access_token

    async def load(self):
        google_conf = self._request.app['configuration'].google_oauth2
        user_info = await retrieve_google_user_info(google_conf, self._access_token)
        logger.debug('Google user info: %r', user_info)


async def retrieve_google_user_info(*args):
    loop = get_running_loop()
    return await loop.run_in_executor(None, sync_retrieve_google_user_info, *args)


def sync_retrieve_google_user_info(google_conf, access_token):
    google = OAuth2Session(
        client_id=google_conf.client_id,
        token={'access_token': access_token})
    r = google.get(google_conf.user_info_url)
    r.raise_for_status()
    return r.json()

