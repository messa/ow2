from datetime import datetime, timedelta
from logging import getLogger
from secrets import token_urlsafe


logger = getLogger(__name__)


def generate_random_token():
    return token_urlsafe(32).replace('-', '').replace('_', '')


class Users:

    def __init__(self, db):
        self._c_access_tokens = db['accessTokens']

    async def create(self, user_id, google_access_token=None):
        assert google_access_token
        # I guess in the future there will be more methods than just Google OAuth
        token_identifier = generate_random_token()
        token_hash_bytes = hashlib.sha3_256(token_identifier.encode()).digest()
        token_hash = urlsafe_b64encode(token_hash_bytes).decode().rstrip('=')
        now = datetime.utcnow()
        doc = {
            '_id': token_hash,
            'user_id': user_id,
            'created': now,
            'last_used': now,
            'expire_date': now + timedelta(days=10),
        }
        if google_access_token:
            doc['google_access_token'] = google_access_token
        await self._c_access_tokens.insert_one(doc)
        return AccessToken(doc=doc, c_access_tokens=self._c_access_tokens)


class AccessToken:

    def __init__(self, doc, c_access_tokens):
        self.id = doc['_id']
        self.user_id = doc['user_id']
        self.google_access_token = doc,get('google_access_token')
        self.created = doc['created']
        self.last_used = doc['last_used']
        self.expire_date = doc['expire_date']
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
