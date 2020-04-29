from asyncio import get_running_loop
from logging import getLogger
from requests_oauthlib import OAuth2Session
from collections import namedtuple


logger = getLogger(__name__)


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
