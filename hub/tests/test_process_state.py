from functools import partial
from pytest import fixture, mark
from simplejson import loads as json_loads
from textwrap import dedent
from yaml import safe_dump as yaml_dump
from yaml import safe_load as yaml_load


@fixture
def sample_snapshot_data():
    return yaml_load('''
        date: "2019-04-01T00:30:00Z"
        label:
            agent: system
            host: example.com
        state:
            load: 1.2
            uptime:
                __value: 3600
                __unit: seconds
            disk_free:
                __value: 10000000
                __unit: bytes
                __check:
                    color: green
            watchdog:
                __watchdog:
                    deadline: 1554079810123 # 2019-04-01 00:50:10.123000
    ''')


@fixture
async def sample_snapshot_loaded(model, sample_snapshot_data):
    assert await model.streams.list_all() == []
    await model.save_report(sample_snapshot_data)


@mark.asyncio
async def test_stream_is_created(model, sample_snapshot_loaded):
    stream, = await model.streams.list_all()
    assert stream.label == {'agent': 'system', 'host': 'example.com'}


@mark.asyncio
async def test_stream_snapshots_get_latest(model, sample_snapshot_loaded,):
    stream, = await model.streams.list_all()
    snapshot = await model.stream_snapshots.get_latest(stream_id=stream.id)
    assert snapshot.stream_id == stream.id
    assert snapshot.date.isoformat() == '2019-04-01T00:30:00+00:00'
    assert yaml_dump(json_loads(snapshot.state_json)) == dedent('''\
        disk_free:
          __check: {color: green}
          __unit: bytes
          __value: 10000000
        load: 1.2
        uptime: {__unit: seconds, __value: 3600}
        watchdog:
          __watchdog: {deadline: 1554079810123}
    ''')


@mark.asyncio
async def test_graphql_streams(model, sample_snapshot_loaded, graphql, remove_ids):
    query = '''
        query TestQuery {
            streams {
                edges {
                    node {
                        streamId
                        labelJSON
                        lastSnapshotDate
                        lastSnapshot {
                            snapshotId
                            streamId
                            date
                            stateItems {
                                path
                                valueJSON
                                checkJSON
                                watchdogJSON
                                unit
                                isCounter
                            }
                        }
                    }
                }
            }
        }
    '''
    data = await graphql(query)
    data = remove_ids(data)
    assert yaml_dump(data) == dedent('''\
        streams:
          edges:
          - node:
              labelJSON: '{"agent":"system","host":"example.com"}'
              lastSnapshot:
                date: '2019-04-01T00:30:00+00:00'
                snapshotId: snapshotId001
                stateItems:
                - checkJSON: null
                  isCounter: null
                  path: [load]
                  unit: null
                  valueJSON: '1.2'
                  watchdogJSON: null
                - checkJSON: null
                  isCounter: null
                  path: [uptime]
                  unit: seconds
                  valueJSON: '3600'
                  watchdogJSON: null
                - checkJSON: '{"color": "green"}'
                  isCounter: null
                  path: [disk_free]
                  unit: bytes
                  valueJSON: '10000000'
                  watchdogJSON: null
                - checkJSON: null
                  isCounter: null
                  path: [watchdog]
                  unit: null
                  valueJSON: null
                  watchdogJSON: '{"deadline": 1554079810123}'
                streamId: streamId000
              lastSnapshotDate: '2019-04-01T00:30:00+00:00'
              streamId: streamId000
    ''')
