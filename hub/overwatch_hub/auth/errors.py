from logging import getLogger


logger = getLogger(__name__)


class AuthError (Exception):
    '''
    This is for logic errors, like invalid client id, expired access token etc.
    Not for transport issues like HTTP status 500 or connection timeout.
    '''
    pass

