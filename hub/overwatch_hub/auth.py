from asyncio import get_running_loop
from collections import namedtuple
from logging import getLogger
from urllib.parse import unquote
from requests_oauthlib import OAuth2Session


logger = getLogger(__name__)

token_cookie_name = 'ow2token'


class AuthError (Exception):
    '''
    This is for logic errors, like invalid client id, expired access token etc.
    Not for transport issues like HTTP status 500 or connection timeout.
    '''
    pass


async def login_via_google_oauth2_token(google_access_token, configuration, model):
    user_info = await retrieve_google_user_info(
        google_conf=configuration.google_oauth2,
        access_token=google_access_token)
    assert isinstance(user_info, dict)
    logger.debug('Google user info: %r', user_info)
    # How user_info looks like:
    # {
    #     'id': '104709048199562099011',
    #     'email': 'petr@leadhub.co',
    #     'verified_email': True,
    #     'name': 'Petr Messner',
    #     'given_name': 'Petr',
    #     'family_name': 'Messner',
    #     'picture': 'https://lh3.googleusercontent.com/a-/AAuE7mC09RdSBW68zYYYpb9TBnPEyC7oPagBHArbLPRI',
    #     'locale': 'cs',
    #     'hd': 'leadhub.co'
    # }
    if user_info['verified_email'] != True:
        raise AuthError('verified_email is not True')
    email_ok = configuration.google_oauth2.validate_email_address(user_info['email'], hd=user_info.get('hd'))
    if not email_ok:
        raise AuthError(f"E-mail address {user_info['email']} not accepted")
    user = await model.users.get_or_create_google_user(
        google_id=user_info['id'],
        display_name=user_info['name'],
        email_address=user_info['email'])
    logger.debug('User: %r', user)
    token = await model.access_tokens.create(user_id=user.id, google_access_token=google_access_token)
    return LoginViaGoogleResult(user=user, token=token)


LoginViaGoogleResult = namedtuple('LoginViaGoogleResult', 'user token')


async def get_user(request):
    if 'user' not in request:
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


async def retrieve_google_user_info(google_conf, access_token):
    loop = get_running_loop()
    return await loop.run_in_executor(None, sync_retrieve_google_user_info, google_conf, access_token)


def sync_retrieve_google_user_info(google_conf, access_token):
    google = OAuth2Session(
        client_id=google_conf.client_id,
        token={'access_token': access_token, 'token_type': 'Bearer'})
    r = google.get(google_conf.user_info_url)
    r.raise_for_status()
    return r.json()

