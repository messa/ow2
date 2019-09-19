from logging import getLogger

from ..util import random_str


logger = getLogger(__name__)


class Users:

    def __init__(self, db):
        self._c_users = db['users']

    async def create_mandatory_indexes(self):
        await self._c_users.create_index('google_id', unique=True, sparse=True)

    async def get_or_create_google_user(self, google_id, display_name, email_address):
        assert google_id
        assert isinstance(google_id, str)
        q = {'google_id': google_id}
        doc = await self._c_users.find_one(q)
        if not doc:
            doc = {
                '_id': random_str(8),
                'google_id': google_id,
                'display_name': display_name,
                'email_address': email_address,
            }
            await self._c_users.insert_one(doc)
        return User(doc=doc)


class User:

    def __init__(self, doc):
        self.id = doc['_id']
        self.google_id = doc.get('google_id')
        self.display_name = doc.get('display_name')
        self.email_address = doc.get('email_address')

    def __repr__(self):
        return f'<{self.__class__.__name} id={self.id!r} display_name={self.display_name!r}>'