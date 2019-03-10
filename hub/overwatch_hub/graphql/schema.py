from logging import getLogger
from graphql import (
    graphql,
    GraphQLSchema,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLField,
    GraphQLInputObjectField,
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
    GraphQLID,
    GraphQLBoolean,
)

from .relay_helpers import connection_args, connection_from_list, relay_connection_type, mutation


logger = getLogger(__name__)


async def node_resolver():
    raise NotImplementedError()


def resolve_node_type(obj, info):
    # See also: https://stackoverflow.com/q/34726666/196206
    # if obj.node_type == 'Post':
    #     return Post
    # if obj.node_type == 'Category':
    #     return Category
    raise Exception(f'Unknown node type: {obj!r}')


NodeInterface = GraphQLInterfaceType(
    name='Node',
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
    },
    resolve_type=resolve_node_type)


Schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='Query',
        fields={
            'node': GraphQLField(
                type=NodeInterface,
                args={
                    'id': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                },
                resolver=node_resolver),
            # 'categories': GraphQLField(
            #     type=CategoryConnection,
            #     args=connection_args,
            #     resolver=categories_resolver),
        }
    ),
)
