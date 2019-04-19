import React from 'react'
import { withRouter } from 'next/router'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Container from '../components/ui/Container'
import Tabs from '../components/ui/Tabs'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import SnapshotHistory from '../components/SnapshotHistory'
import LabelFromJSON from '../components/util/LabelFromJSON'
import DateTime from '../components/util/DateTime'

class StreamsPage extends React.Component {

  render() {
    const { stream, historySnapshot } = this.props
    const { query } = this.props.router
    const showTab = query['tab'] || 'lastSnapshot'
    const { historySnapshotId } = query
    const { streamId, lastSnapshot, lastSnapshotDate } = stream
    const lastSnapshotState = lastSnapshot && JSON.parse(lastSnapshot.stateJSON)
    const historySnapshotState = historySnapshot && JSON.parse(historySnapshot.stateJSON)
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
          <pre>{JSON.stringify({ lastSnapshotState }, null, 4)}</pre>
        )}

        {showTab === 'history' && (
          <div style={{ display: 'flex' }}>
            <div>
              <SnapshotHistory
                snapshots={snapshots}
                activeSnapshotId={historySnapshotId}
              />
            </div>
            <div style={{ marginLeft: 25 }}>
              {historySnapshotState && (
                <pre>{JSON.stringify({ historySnapshotState }, null, 4)}</pre>
              )}
            </div>
          </div>

        )}

        </Container>
      </Layout>
    )
  }

}

export default withData(withRouter(StreamsPage), {
  variables: ({ query }) => ({
    streamId: query.id,
    getLastSnapshot: !query.tab,
    getSnapshots: query.tab === 'history',
    getHistorySnapshot: !!query.historySnapshotId,
    historySnapshotId: query.historySnapshotId || '',
  }),
  query: graphql`
    query streamQuery(
      $streamId: String!,
      $getLastSnapshot: Boolean!,
      $getSnapshots: Boolean!,
      $getHistorySnapshot: Boolean!,
      $historySnapshotId: String!,
    ) {
      stream(streamId: $streamId) {
        id
        streamId
        labelJSON
        lastSnapshotDate
        lastSnapshot @include(if: $getLastSnapshot) {
          date
          stateJSON
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
      historySnapshot: streamSnapshot(snapshotId: $historySnapshotId) @include(if: $getHistorySnapshot) {
        id
        snapshotId
        streamId
        date
        stateJSON
      }
    }
  `
})
