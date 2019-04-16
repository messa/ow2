import asyncio
from graphene import ObjectType, Field, Int, String, Schema, DateTime
from graphene.relay import Node, Connection, ConnectionField
from graphene.types.json import JSONString
from logging import getLogger

from .helpers import Obj, json_dumps


logger = getLogger(__name__)


'''
class Record (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    record_id = String(name='recordId')
    pack_id = String(name='packId')
    record = JSONString()

    #pack = lambda: Pack()

    def resolve_record_id(record, info):
        return str(record.id)


class RecordConnection (Connection):

    class Meta:
        node = Record
'''

'''
class Pack (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    label_json = String(name='labelJSON')
    pack_id = String(name='packId')
    records = ConnectionField(RecordConnection)
    fresh_record_count = Int()

    def resolve_pack_id(root, info):
        return root.id

    async def resolve_records(pack, info):
        model = info.context['request'].app['model']
        records = await model.fresh_records.list_by_pack_id(pack.id)
        return records

    async def resolve_fresh_record_count(pack, info):
        model = info.context['request'].app['model']
        return await model.fresh_records.count_by_pack_id(pack.id)


class PackConnection (Connection):

    class Meta:
        node = Pack
'''


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

    stream = Field(lambda: Stream)

    def resolve_snapshot_id(snapshot, info):
        return snapshot.id

    async def resolve_stream(snapshot, info):
        model = get_model(info)
        stream = await model.streams.get_by_id(snapshot.stream_id)
        return stream


class Stream (ObjectType):

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        raise Exception('NIY')

    label_json = String(name='labelJSON')
    stream_id = String(name='streamId')
    last_snapshot = Field(StreamSnapshot, name='lastSnapshot')

    def resolve_stream_id(stream, info):
        return stream.id

    def resolve_label_json(stream, info):
        return json_dumps(stream.label)

    async def resolve_last_snapshot(stream, info):
        model = get_model(info)
        snapshot = await model.stream_snapshots.get_latest(stream_id=stream.id)
        return snapshot


class StreamConnection (Connection):

    class Meta:
        node = Stream


class Query (ObjectType):

    node = Node.Field()

    stream = Field(Stream, stream_id=String(required=True))
    streams = ConnectionField(StreamConnection)

    async def resolve_stream(root, info, stream_id):
        model = get_model(info)
        stream = await model.streams.get_by_id(stream_id)
        return stream

    async def resolve_streams(root, info):
        model = get_model(info)
        streams = await model.streams.list_all()
        return streams


def get_model(info):
    return info.context['request'].app['model']


graphql_schema = Schema(query=Query)
