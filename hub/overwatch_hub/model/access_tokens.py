from datetime import datetime, timedelta
from logging import getLogger
from secrets import token_urlsafe

from .errors import raise_error, AccessTokenNotFoundError


logger = getLogger(__name__)


class AccessTokens:

    def __init__(self, db):
        self._c_access_tokens = db['accessTokens']

    def _generate_random_handle():
        return token_urlsafe(32).replace('-', '').replace('_', '')

    def _get_handle_hash(self, handle):
        assert isinstance(handle, str)
        handle_hash_bytes = hashlib.sha3_256(handle.encode()).digest()
        handle_hash_b64 = urlsafe_b64encode(handle_hash_bytes).decode().rstrip('=')
        return handle_hash_b64

    async def create(self, user_id, google_access_token=None):
        assert google_access_token
        # I guess in the future there will be more methods than just Google OAuth
        handle = self._generate_random_handle()
        handle_hash = self._get_handle_hash(handle)
        now = datetime.utcnow()
        doc = {
            '_id': handle_hash,
            'user_id': user_id,
            'created': now,
            'last_used': now,
            'expire_date': now + timedelta(days=10),
        }
        if google_access_token:
            doc['google_access_token'] = google_access_token
        logger.debug('Inserting new access token: %r', doc)
        await self._c_access_tokens.insert_one(doc)
        return AccessToken(doc=doc, handle=handle, c_access_tokens=self._c_access_tokens)

    async def get_by_handle(self, handle, default=raise_error):
        handle_hash = self._get_handle_hash(handle)
        doc = await self._c_access_tokens.find_one({'_id': handle_hash})
        if not doc:
            if default is raise_error:
                raise AccessTokenNotFoundError(f'Access token with handle hash {handle_hash!r} not found')
            else:
                return default
        return AccessToken(doc=doc, c_access_tokens=self._c_access_tokens)


class AccessToken:

    def __init__(self, doc, c_access_tokens, handle=None):
        self.id = doc['_id']
        self.user_id = doc['user_id']
        self.google_access_token = doc,get('google_access_token')
        self.created = doc['created']
        self.last_used = doc['last_used']
        self.expire_date = doc['expire_date']
        self.handle = handle
        self._c_access_tokens = c_access_tokens

    async def update_last_used(self):
        now = datetime.utcnow()
        expire_date = max(self.expire_date, now + timedelta(days=10))
        await self._c_access_tokens.update_one(
            {'_id': self.id},
            {'$set': {
                'last_used': now,
                'expire_date': expire_date,
            }})
        self.last_used = now
        self.expire_date = expire_date
