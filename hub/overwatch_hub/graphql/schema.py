import asyncio
from graphene import Schema, ObjectType, Field, List
from graphene import Int, String, DateTime, Boolean
from graphene.relay import Node, Connection, ConnectionField
from graphene.types.json import JSONString
from logging import getLogger

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
    current_value_json = JSONString(name='currentValueJSON')
    check_json = JSONString(name='checkJSON')
    watchdog_json = JSONString(name='watchdogJSON')
    is_counter = Boolean()
    unit = String()
    stream_id = String()
    stream = Field(lambda: Stream)
    snapshot_id = String()
    snapshot = Field(lambda: StreamSnapshot)

    def resolve_id(item, info):
        from random import random
        return str(random())

    def resolve_path(item, info):
        return item['path']

    def resolve_path_str(item, info):
        return ' > '.join(item['path'])

    def resolve_key(item, info):
        return item['key']

    def resolve_value_json(item, info):
        return item.get('value')

    def resolve_unit(item, info):
        return item.get('unit')

    def resolve_is_counter(item, info):
        if item.get('counter') == None:
            return None
        return bool(item['counter'])

    def resolve_check_json(item, info):
        return item.get('check')

    def resolve_watchdog_json(item, info):
        return item.get('watchdog')

    def resolve_stream(item, info):
        raise Exception('NIY: SnapshotItem resolve_stream')

    def resolve_snapshot(item, info):
        raise Exception('NIY: SnapshotItem resolve_snapshot')


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
    date = DateTime()
    state_json = String(name='stateJSON')
    state_items = List(SnapshotItem)

    stream = Field(lambda: Stream)

    def resolve_snapshot_id(snapshot, info):
        return snapshot.id

    async def resolve_stream(snapshot, info):
        model = get_model(info)
        stream = await model.streams.get_by_id(snapshot.stream_id)
        return stream

    def resolve_state_items(snapshot, info):
        logger.debug('StreamSnapshot %r resolve_state_items -> %r', snapshot, snapshot.state_items_flat)
        return snapshot.state_items_flat


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
        snapshot = await model.stream_snapshots.get_latest_metadata(stream_id=stream.id)
        return snapshot.date

    async def resolve_snapshots(stream, info):
        model = get_model(info)
        snapshots = await model.stream_snapshots.list_metadata(stream_id=stream.id)
        return snapshots


class StreamConnection (Connection):

    class Meta:
        node = Stream


class Query (ObjectType):

    node = Node.Field()

    stream = Field(Stream, stream_id=String(required=True))
    streams = ConnectionField(StreamConnection)
    stream_snapshot = Field(StreamSnapshot, snapshot_id=String(required=True))
    search_current_snapshot_items = Field(SnapshotItemConnection, path_query=String(required=True))

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

    async def resolve_search_current_snapshot_items(root, info, path_query):
        model = get_model(info)
        streams = await model.streams.list_all()
        stream_ids = [s.id for s in streams]
        snapshots = await model.strean_snapshots.get_by_ids(stream_ids)
        found_items = []
        for snapshot in snapshots:
            found_items.extend(snapshot.search_items(path_query=path_query))
        return found_items


def get_model(info):
    if 'request' in info.context:
        return info.context['request'].app['model']
    return info.context['model']


graphql_schema = Schema(query=Query)
