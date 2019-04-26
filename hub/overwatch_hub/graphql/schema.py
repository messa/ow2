import asyncio
from graphene import Schema, ObjectType, Field, List
from graphene import Int, String, DateTime, Boolean
from graphene.relay import Node, Connection, ConnectionField
from graphene.types.json import JSONString
from logging import getLogger
import re
from simplejson import loads as json_loads
from time import time
from time import monotonic as monotime

from .helpers import Obj, json_dumps


logger = getLogger(__name__)


class StreamSnapshotMetadata (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    snapshot_id = String(name='snapshotId')
    stream_id = String(name='streamId')
    date = DateTime()

    stream = Field(lambda: Stream)

    def resolve_snapshot_id(snapshot, info):
        return snapshot.id

    async def resolve_stream(snapshot, info):
        model = get_model(info)
        stream = await model.streams.get_by_id(snapshot.stream_id)
        return stream


class StreamSnapshotMetadataConnection (Connection):

    class Meta:
        node = StreamSnapshotMetadata


class SnapshotItem (ObjectType):

    class Meta:
        interfaces = (Node, )

    path = List(String)
    path_str = String(name='pathStr')
    key = String()
    value_json = JSONString(name='valueJSON')
    check_json = JSONString(name='checkJSON')
    check_state = String()
    watchdog_json = JSONString(name='watchdogJSON')
    watchdog_expired = Boolean()
    is_counter = Boolean()
    unit = String()
    stream_id = String()
    stream = Field(lambda: Stream)
    snapshot_id = String()
    snapshot_date = DateTime()
    snapshot = Field(lambda: StreamSnapshot)

    def resolve_id(item, info):
        return f'{item.snapshot_id}:{item.path_str}'

    def resolve_path(item, info):
        return item.path

    def resolve_path_str(item, info):
        return ' > '.join(item['path'])

    def resolve_key(item, info):
        return item.key

    def resolve_value_json(item, info):
        return item.value

    def resolve_is_counter(item, info):
        return item.is_counter

    def resolve_check_json(item, info):
        return item.raw_check

    def resolve_watchdog_json(item, info):
        return item.raw_watchdog

    def resolve_stream_id(item, info):
        return item.stream_id

    async def resolve_stream(item, info):
        model = get_model(info)
        return await model.streams.get_by_id(item.stream_id)

    def resolve_snapshot_id(item, info):
        assert item.snapshot_id
        return item.snapshot_id

    def resolve_snapshot_date(item, info):
        assert item.snapshot_date
        return item.snapshot_date

    async def resolve_snapshot(item, info):
        model = get_model(info)
        return await model.stream_snapshots.get_by_id(item.snapshot_id)


class SnapshotItemConnection (Connection):

    class Meta:
        node = SnapshotItem


class StreamSnapshot (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    snapshot_id = String(name='snapshotId')
    stream_id = String(name='streamId')
    stream = Field(lambda: Stream)
    date = DateTime()
    state_json = String(name='stateJSON')
    state_items = List(SnapshotItem)
    green_check_items = List(SnapshotItem)
    red_check_items = List(SnapshotItem)
    green_check_count = Int()
    red_check_count = Int()

    def resolve_snapshot_id(snapshot, info):
        return snapshot.id

    async def resolve_stream(snapshot, info):
        model = get_model(info)
        stream = await model.streams.get_by_id(snapshot.stream_id)
        return stream

    async def resolve_state_json(snapshot, info):
        await snapshot.load_state()
        return snapshot.state_json

    async def resolve_state_items(snapshot, info):
        await snapshot.load_state()
        return snapshot.state_items

    async def resolve_green_check_items(snapshot, info):
        await snapshot.load_state()
        return snapshot.green_check_items

    async def resolve_red_check_items(snapshot, info):
        await snapshot.load_state()
        return snapshot.red_check_items

    async def resolve_green_check_count(snapshot, info):
        await snapshot.load_state()
        green_count = 0
        for item in snapshot.green_check_items:
            if item.check_state == 'green':
                green_count += 1
            if item.watchdog_expired == False:
                green_count += 1
        return green_count

    async def resolve_red_check_count(snapshot, info):
        await snapshot.load_state()
        red_count = 0
        for item in snapshot.red_check_items:
            if item.check_state == 'red':
                red_count += 1
            if item.watchdog_expired == True:
                red_count += 1
        return red_count


class Stream (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    label_json = String(name='labelJSON')
    stream_id = String(name='streamId')
    last_snapshot = Field(StreamSnapshot, name='lastSnapshot')
    last_snapshot_date = DateTime(name='lastSnapshotDate')
    snapshots = ConnectionField(StreamSnapshotMetadataConnection)
    item_history = ConnectionField(SnapshotItemConnection, path=List(String, required=True))

    def resolve_stream_id(stream, info):
        return stream.id

    def resolve_label_json(stream, info):
        return json_dumps(stream.label, sort_keys=True)

    async def resolve_last_snapshot(stream, info):
        model = get_model(info)
        snapshot = await model.stream_snapshots.get_latest(stream_id=stream.id)
        return snapshot

    async def resolve_last_snapshot_date(stream, info):
        model = get_model(info)
        snapshot = await model.stream_snapshots.get_latest(stream_id=stream.id)
        return snapshot.date

    async def resolve_snapshots(stream, info):
        model = get_model(info)
        snapshots = await model.stream_snapshots.list_by_stream_id(stream_id=stream.id)
        return snapshots

    async def resolve_item_history(stream, info, path):
        model = get_model(info)
        snapshots = await model.stream_snapshots.list_by_stream_id(stream_id=stream.id)
        logger.debug('Found %d snapshots for stream %s', len(snapshots), stream.id)
        snapshots = snapshots[:1000]
        path_str = ' > '.join(path)
        sem = asyncio.Semaphore(16)
        async def _get_hist(snapshot):
            async with sem:
                await snapshot.load_state()
                for item in snapshot.state_items:
                    if item.path_str == path_str:
                        return item
                return None
        t = monotime()
        items = await asyncio.gather(*[_get_hist(sn) for sn in snapshots])
        items = [item for item in items if item is not None]
        logger.debug(
            'Searched %d stream snapshot states in %.3f s, found %d items',
            len(snapshots), monotime() - t, len(items))
        return items


class StreamConnection (Connection):

    class Meta:
        node = Stream


class Alert (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    alert_id = String()
    stream_id = String()
    stream = Field(Stream)
    alert_type = String()
    item_path = List(String)
    first_snapshot_id = String()
    first_snapshot_date = DateTime()
    last_snapshot_id = String()
    last_snapshot_date = DateTime()
    first_item_value_json = JSONString(name='firstItemValueJSON')
    last_item_value_json = JSONString(name='lastItemValueJSON')
    first_item_unit = String()
    last_item_unit = String()

    def resolve_alert_id(alert, info):
        return alert.id

    async def resolve_stream(alert, info):
        return get_model(info).streams.get_by_id(alert.stream_id)

    def resolve_first_item_value_json(alert, info):
        return alert.first_item_value

    def resolve_last_item_value_json(alert, info):
        return alert.last_item_value


class AlertConnection (Connection):

    class Meta:
        node = Alert


class Query (ObjectType):

    node = Node.Field()

    stream = Field(Stream, stream_id=String(required=True))
    streams = ConnectionField(StreamConnection)
    stream_snapshot = Field(StreamSnapshot, snapshot_id=String(required=True))
    last_stream_snapshot = Field(StreamSnapshot, stream_id=String(required=True))
    search_current_snapshot_items = ConnectionField(SnapshotItemConnection, path_query=String(required=True))
    active_alerts = ConnectionField(AlertConnection)
    inactive_alerts = ConnectionField(AlertConnection)
    alert = Field(Alert, alert_id=String(required=True))

    async def resolve_stream(root, info, stream_id):
        model = get_model(info)
        stream = await model.streams.get_by_id(stream_id)
        return stream

    async def resolve_streams(root, info):
        model = get_model(info)
        streams = await model.streams.list_all()
        return streams

    async def resolve_stream_snapshot(root, info, snapshot_id):
        model = get_model(info)
        snapshot = await model.stream_snapshots.get_by_id(snapshot_id)
        return snapshot

    async def resolve_last_stream_snapshot(root, info, stream_id):
        model = get_model(info)
        snapshot = await model.stream_snapshots.get_latest(stream_id=stream_id)
        return snapshot

    async def resolve_search_current_snapshot_items(root, info, path_query):
        model = get_model(info)
        t = monotime()
        streams = await model.streams.list_all()
        snapshot_ids = [s.last_snapshot_id for s in streams]
        snapshots = await model.stream_snapshots.get_by_ids(snapshot_ids, load_state=True)
        re_pq = re.compile(path_query)
        found_items = []
        for snapshot in snapshots:
            for item in snapshot.state_items:
                if re_pq.match(item.path_str):
                    found_items.append(item)
            if len(found_items) >= 10000:
                logger.debug('Too many found_items')
                break
        logger.debug(
            'resolve_search_current_snapshot_items %r found %s items in %.3f s',
            path_query, len(found_items), monotime() - t)
        return found_items

    async def resolve_active_alerts(root, info):
        return await get_model(info).alerts.list_active()

    async def resolve_inactive_alerts(root, info):
        return await get_model(info).alerts.list_inactive()

    async def resolve_alert(root, info, alert_id):
        return await get_model(info).alerts.get_by_id(alert_id)



def get_model(info):
    if 'request' in info.context:
        return info.context['request'].app['model']
    return info.context['model']


graphql_schema = Schema(query=Query)
