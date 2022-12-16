from functools import partial
import pytest_asyncio
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


@pytest_asyncio.fixture
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
    await snapshot.load_state()
    assert snapshot.stream_id == stream.id
    assert snapshot.date.isoformat() == '2019-04-01T00:30:00+00:00'
    assert yaml_dump(json_loads(snapshot.state_json)) == dedent('''\
        disk_free:
          __check:
            color: green
          __unit: bytes
          __value: 10000000
        load: 1.2
        uptime:
          __unit: seconds
          __value: 3600
        watchdog:
          __watchdog:
            deadline: 1554079810123
    ''')


@mark.asyncio
async def test_alert_is_created(model, sample_snapshot_loaded):
    assert await model.alerts.list_inactive() == []
    active_alert, = await model.alerts.list_active()
    assert active_alert.alert_type == 'watchdog'
    assert active_alert.item_path == ('watchdog', )
    assert await model.alerts.get_by_id(active_alert.id)


@mark.asyncio
async def test_graphql_streams(model, sample_snapshot_loaded, graphql, remove_ids):
    query = '''
        query TestQuery {
            activeUnacknowledgedAlerts {
                edges {
                    node {
                        alertId
                        streamId
                        alertType
                        itemPath
                        firstSnapshotId
                        lastSnapshotId
                    }
                }
            }
            activeAcknowledgedAlerts {
                edges {
                    node {
                        alertId
                    }
                }
            }
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
                            greenCheckCount
                            redCheckCount
                            stateItems {
                                path
                                key
                                valueJSON
                                checkJSON
                                checkState
                                watchdogJSON
                                watchdogExpired
                                unit
                                isCounter
                                streamId
                                snapshotId
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
        activeAcknowledgedAlerts:
          edges: []
        activeUnacknowledgedAlerts:
          edges:
          - node:
              alertId: alertId000
              alertType: watchdog
              firstSnapshotId: snapshotId000
              itemPath:
              - watchdog
              lastSnapshotId: snapshotId000
              streamId: streamId000
        streams:
          edges:
          - node:
              labelJSON: '{"agent":"system","host":"example.com"}'
              lastSnapshot:
                date: '2019-04-01T00:30:00+00:00'
                greenCheckCount: 1
                redCheckCount: 1
                snapshotId: snapshotId000
                stateItems:
                - checkJSON: null
                  checkState: null
                  isCounter: false
                  key: load
                  path:
                  - load
                  snapshotId: snapshotId000
                  streamId: streamId000
                  unit: null
                  valueJSON: '1.2'
                  watchdogExpired: null
                  watchdogJSON: null
                - checkJSON: null
                  checkState: null
                  isCounter: false
                  key: uptime
                  path:
                  - uptime
                  snapshotId: snapshotId000
                  streamId: streamId000
                  unit: seconds
                  valueJSON: '3600'
                  watchdogExpired: null
                  watchdogJSON: null
                - checkJSON: '{"color": "green"}'
                  checkState: green
                  isCounter: false
                  key: disk_free
                  path:
                  - disk_free
                  snapshotId: snapshotId000
                  streamId: streamId000
                  unit: bytes
                  valueJSON: '10000000'
                  watchdogExpired: null
                  watchdogJSON: null
                - checkJSON: null
                  checkState: null
                  isCounter: false
                  key: watchdog
                  path:
                  - watchdog
                  snapshotId: snapshotId000
                  streamId: streamId000
                  unit: null
                  valueJSON: null
                  watchdogExpired: true
                  watchdogJSON: '{"deadline": 1554079810123}'
                streamId: streamId000
              lastSnapshotDate: '2019-04-01T00:30:00+00:00'
              streamId: streamId000
    ''')
