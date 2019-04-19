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
    const { stream } = this.props
    const { query } = this.props.url
    const showTab = query['tab'] || 'lastSnapshot'
    const { streamId, lastSnapshot, lastSnapshotDate } = stream
    const lastSnapshotState = lastSnapshot && JSON.parse(lastSnapshot.stateJSON)
    const snapshots = stream.snapshots && stream.snapshots.edges.map(edge => edge.node)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Stream <code>{stream.streamId}</code></h1>

          <div class="row">
            <div class="eight columns">
              <LabelFromJSON labelJSON={stream.labelJSON} />
            </div>
            <div class="four columns text-right">
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
          <SnapshotHistory snapshots={snapshots} />
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
  }),
  query: graphql`
    query streamQuery(
      $streamId: String!,
      $getLastSnapshot: Boolean!,
      $getSnapshots: Boolean!
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
    }
  `
})
