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


async def get_auth_context(request):
    if 'auth_context' not in request:
        request['auth_context'] = await do_get_auth_context(request)
    return request['auth_context']


async def do_get_auth_context(request):
    conf = request.app['configuration']
    model = request.app['model']
    access_token_handle = get_request_access_token_handle(request, conf)
    if access_token_handle:
        access_token = model.access_tokens.get_by_handle(access_token_handle, default=None)
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
    pass


class UserAuthContext:
    pass


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

