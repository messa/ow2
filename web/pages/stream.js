import React from 'react'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Container from '../components/ui/Container'
import Tabs from '../components/ui/Tabs'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import SnapshotHistory from '../components/SnapshotHistory'
import LabelFromJSON from '../components/util/LabelFromJSON'
import DateTime from '../components/util/DateTime'
import StreamSnapshot from '../components/streamSnapshot/StreamSnapshot'

class StreamPage extends React.Component {

  static async getInitialProps({ query }) {
    return {
      streamId: query['id'],
      showTab: query['tab'] || 'lastSnapshot',
      stateView: query['stateView'] || 'nested',
      historySnapshotId: query['historySnapshotId'],
      historyStateView: query['historyStateView'] || 'nested',
    }
  }

  render() {
    const {
      stream, historySnapshot, showTab, stateView,
      historySnapshotId, historyStateView
    } = this.props
    //const { query } = this.props.router
    //const showTab = query['tab'] || 'lastSnapshot'
    //const stateView = query['stateView'] || 'nested'
    //const { historySnapshotId } = query
    const { streamId, lastSnapshot, lastSnapshotDate } = stream
    //const lastSnapshotState = lastSnapshot && JSON.parse(lastSnapshot.stateJSON)
    //const historySnapshotState = historySnapshot && JSON.parse(historySnapshot.stateJSON)
    const snapshots = stream.snapshots && stream.snapshots.edges.map(edge => edge.node)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Stream <code>{stream.streamId}</code></h1>

          <div className="row">
            <div className="eight columns">
              <LabelFromJSON labelJSON={stream.labelJSON} />
            </div>
            <div className="four columns text-right">
              <DateTime value={lastSnapshotDate} />
            </div>
           </div>

          <Tabs
            activeKey={showTab}
            items={[
              {
                key: 'lastSnapshot',
                title: 'Last snapshot',
                href: {
                  pathname: '/stream',
                  query: { 'id': streamId },
                }
              }, {
                key: 'history',
                title: 'History',
                href: {
                  pathname: '/stream',
                  query: { 'id': streamId, 'tab': 'history' },
                }
              },
            ]}
          />

        {showTab === 'lastSnapshot' && (
          <StreamSnapshot
            key={lastSnapshot.id}
            snapshot={lastSnapshot}
            stateView={stateView}
            nestedViewHref={{
              pathname: '/stream',
              query: {
                'id': streamId,
              }
            }}
            flatViewHref={{
              pathname: '/stream',
              query: {
                'id': streamId,
                'stateView': 'flat',
              }
            }}
            jsonViewHref={{
              pathname: '/stream',
              query: {
                'id': streamId,
                'stateView': 'json',
              }
            }}
          />
        )}

        {showTab === 'history' && (
          <div style={{ display: 'flex' }}>
            <div>
              <SnapshotHistory
                snapshots={snapshots}
                activeSnapshotId={historySnapshotId}
              />
            </div>
            <div style={{ marginLeft: 25, flexGrow: 1 }}>
              {historySnapshot && (
                <StreamSnapshot
                  key={historySnapshot.id}
                  snapshot={historySnapshot}
                  stateView={historyStateView}
                  nestedViewHref={{
                    pathname: '/stream',
                    query: {
                      'id': streamId,
                      'tab': 'history',
                      'historySnapshotId': historySnapshotId,
                    }
                  }}
                  flatViewHref={{
                    pathname: '/stream',
                    query: {
                      'id': streamId,
                      'tab': 'history',
                      'historySnapshotId': historySnapshotId,
                      'historyStateView': 'flat',
                    }
                  }}
                  jsonViewHref={{
                    pathname: '/stream',
                    query: {
                      'id': streamId,
                      'tab': 'history',
                      'historySnapshotId': historySnapshotId,
                      'historyStateView': 'json',
                    }
                  }}
                />
              )}
            </div>
          </div>

        )}

        </Container>
      </Layout>
    )
  }

}

export default withData(
  StreamPage,
  {
    variables: ({ query }, { streamId, showTab, stateView, historySnapshotId, historyStateView }) => ({
      streamId,
      getLastSnapshot: showTab === 'lastSnapshot',
      getLastSnapshotJSON: showTab === 'lastSnapshot' && stateView === 'json',
      getLastSnapshotItems: showTab === 'lastSnapshot' && stateView !== 'json',
      getSnapshots: showTab === 'history',
      getHistorySnapshot: showTab === 'history' && !!historySnapshotId,
      getHistorySnapshotJSON: showTab === 'history' && historyStateView === 'json',
      getHistorySnapshotItems: showTab === 'history' && historyStateView !== 'json',
      historySnapshotId: historySnapshotId || '',
    }),
    query: graphql`
      query streamQuery(
        $streamId: String!,
        $getLastSnapshot: Boolean!,
        $getLastSnapshotJSON: Boolean!,
        $getLastSnapshotItems: Boolean!,
        $getSnapshots: Boolean!,
        $getHistorySnapshot: Boolean!,
        $getHistorySnapshotJSON: Boolean!,
        $getHistorySnapshotItems: Boolean!,
        $historySnapshotId: String!,
      ) {
        stream(streamId: $streamId) {
          id
          streamId
          labelJSON
          lastSnapshotDate
          lastSnapshot @include(if: $getLastSnapshot) {
            id
            ...StreamSnapshot_snapshot @arguments(
              withJSON: $getLastSnapshotJSON,
              withItems: $getLastSnapshotItems,
            )
          }
          snapshots @include(if: $getSnapshots) {
            edges {
              cursor
              node {
                id
                streamId
                snapshotId
                date
              }
            }
          }
        }
        historySnapshot: streamSnapshot(
          snapshotId: $historySnapshotId
        ) @include(if: $getHistorySnapshot) {
          id
          ...StreamSnapshot_snapshot @arguments(
            withJSON: $getHistorySnapshotJSON,
            withItems: $getHistorySnapshotItems,
          )
        }
      }
    `
  })
