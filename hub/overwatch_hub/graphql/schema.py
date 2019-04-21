import asyncio
from graphene import Schema, ObjectType, Field, List
from graphene import Int, String, DateTime, Boolean
from graphene.relay import Node, Connection, ConnectionField
from graphene.types.json import JSONString
from logging import getLogger
import re
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
        return item.snapshot_id

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

    async def resolve_state_json(snapshot, info):
        await snapshot.load_state()
        return snapshot.state_json

    async def resolve_state_items(snapshot, info):
        await snapshot.load_state()
        return snapshot.state_items


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
        snapshot = await model.stream_snapshots.get_latest(stream_id=stream.id)
        return snapshot.date

    async def resolve_snapshots(stream, info):
        model = get_model(info)
        snapshots = await model.stream_snapshots.list_by_stream_id(stream_id=stream.id)
        return snapshots


class StreamConnection (Connection):

    class Meta:
        node = Stream


class Query (ObjectType):

    node = Node.Field()

    stream = Field(Stream, stream_id=String(required=True))
    streams = ConnectionField(StreamConnection)
    stream_snapshot = Field(StreamSnapshot, snapshot_id=String(required=True))
    search_current_snapshot_items = ConnectionField(SnapshotItemConnection, path_query=String(required=True))

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
        logger.debug(
            'resolve_search_current_snapshot_items %r found %s items in %.3f s',
            path_query, len(found_items), monotime() - t)
        return found_items


def get_model(info):
    if 'request' in info.context:
        return info.context['request'].app['model']
    return info.context['model']


graphql_schema = Schema(query=Query)
