from bson import ObjectId
from datetime import datetime
from logging import getLogger
from pymongo import DESCENDING as DESC
from time import monotonic as monotime

from ..util import random_str, to_utc
from .errors import AlertNotFoundError
from .helpers import to_objectid


logger = getLogger(__name__)


class Alerts:

    def __init__(self, db, alert_webhooks):
        self._alert_webhooks = alert_webhooks
        self._c_active = db['alerts.active']
        self._c_inactive = db['alerts.inactive']

    async def get_by_id(self, alert_id):
        assert isinstance(alert_id, str)
        active = True
        doc = await self._c_active.find_one({'_id': alert_id})
        if not doc:
            active = False
            doc = await self._c_inactive.find_one({'_id': alert_id})
        if not doc:
            raise AlertNotFoundError(alert_id=alert_id)
        return Alert(doc, active=active)

    async def list_active(self):
        docs = await self._c_active.find({}).to_list(length=None)
        return [Alert(doc, active=True) for doc in docs]

    async def list_inactive(self):
        t = monotime()
        docs = await self._c_inactive.find({},
            sort=[('last_snapshot_id', DESC)], limit=100).to_list(length=None)
        logger.debug('Retrieved %d inactive alerts in %.3f s', len(docs), monotime() - t)
        return [Alert(doc, active=False) for doc in docs]

    async def create_or_update_alert(self, stream_id, alert_type, item_path, snapshot_id, snapshot_date, item_value, item_unit):
        assert isinstance(stream_id, str)
        assert isinstance(snapshot_date, datetime)
        assert isinstance(item_path, (list, tuple))
        assert alert_type in ['check', 'watchdog']
        snapshot_id = to_objectid(snapshot_id)
        q = {
            'stream_id': stream_id,
            'alert_type': alert_type,
            'item_path': item_path,
        }
        doc = await self._c_active.find_one(q)
        if not doc:
            doc = {
                '_id': random_str(8),
                **q,
                'first_snapshot_id': snapshot_id,
                'first_snapshot_date': snapshot_date,
                'last_snapshot_id': snapshot_id,
                'last_snapshot_date': snapshot_date,
                'first_item_value': item_value,
                'last_item_value': item_value,
                'first_item_unit': item_unit,
                'last_item_unit': item_unit,
            }
            await self._c_active.insert_one(doc)
            logger.debug('Inserted new alert: %r', doc)
            alert = Alert(doc=doc, active=True)
            if self._alert_webhooks:
                self._alert_webhooks.new_alert_created(alert=alert)
            return
        await self._c_active.update_one(
            {
                '_id': doc['_id'],
                'last_snapshot_id': doc['last_snapshot_id'],
            }, {
                '$set': {
                    'last_snapshot_id': snapshot_id,
                    'last_snapshot_date': snapshot_date,
                    'last_item_value': item_value,
                    'last_item_unit': item_unit,
                },
            })
        logger.debug('Updated alert %s', doc['_id'])

    async def deactivate_alerts(self, stream_id, snapshot_id_ub):
        assert isinstance(stream_id, str)
        snapshot_id_ub = to_objectid(snapshot_id_ub)
        q = {
            'stream_id': stream_id,
            'last_snapshot_id': {'$lt': snapshot_id_ub},
        }
        while True:
            doc = await self._c_active.find_one(q)
            if not doc:
                break
            logger.debug('Deactivating alert %s: %r', doc['_id'], doc)
            await self._c_inactive.replace_one({'_id': doc['_id']}, doc, upsert=True)
            await self._c_active.delete_one({'_id': doc['_id'], 'last_snapshot_id': doc['last_snapshot_id']})
            logger.info('Deactivated alert %s', doc['_id'])
            alert = Alert(doc=doc, active=False)
            if self._alert_webhooks:
                self._alert_webhooks.alert_closed(alert=alert)


class Alert:

    def __init__(self, doc, active):
        self.id = doc['_id']
        self.stream_id = doc['stream_id']
        self.alert_type = doc['alert_type']
        self.item_path = tuple(doc['item_path'])
        self.first_snapshot_id = doc['first_snapshot_id']
        self.first_snapshot_date = to_utc(doc['first_snapshot_date'])
        self.last_snapshot_id = doc['last_snapshot_id']
        self.last_snapshot_date = to_utc(doc['last_snapshot_date'])
        self.first_item_value = doc['first_item_value']
        self.first_item_unit = doc.get('first_item_unit')
        self.last_item_value = doc['last_item_value']
        self.last_item_unit = doc.get('last_item_unit')
        self.active = active

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id!r} alert_type={self.alert_type!r} stream_id={self.stream_id!r} item_path={self.item_path!r}>'
