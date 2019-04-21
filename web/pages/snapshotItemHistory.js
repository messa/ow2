import React from 'react'
import Link from 'next/link'
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
import StreamSnapshot from '../components/streamSnapshot/StreamSnapshot'
import SnapshotItemValue from '../components/streamSnapshot/SnapshotItemValue'

class SnapshotItemHistoryPage extends React.Component {

  static async getInitialProps({ query }) {
    const { streamId } = query
    const itemPath = JSON.parse(query['itemPathJSON'])
    return {
      streamId,
      itemPath,
    }
  }

  render() {
    const { streamId, itemPath, stream } = this.props
    const records = stream.itemHistory.edges.map(edge => edge.node)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item history</h1>

          <p>
            Stream:

            <Link href={{ pathname: '/stream', query: { id: stream.streamId } }}><a>
              <code>{stream.streamId}</code>
            </a></Link>

            &nbsp; &nbsp;

            <LabelFromJSON labelJSON={stream.labelJSON} />
          </p>

          <p>
            Path:
            <code style={{ fontSize: 14 }}>{itemPath.join(' > ')}</code>
          </p>

          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Value</th>
                <th>Snapshot id</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id}>
                  <td><DateTime value={record.snapshotDate} /></td>
                  <td><SnapshotItemValue item={record} /></td>
                  <td><code>{record.snapshotId}</code></td>
                </tr>
              ))}
            </tbody>
          </table>

        </Container>
      </Layout>
    )
  }

}

export default withData(
  SnapshotItemHistoryPage,
  {
    variables: ({ query }, { streamId, itemPath }) => ({
      streamId,
      itemPath,
    }),
    query: graphql`
      query snapshotItemHistoryQuery(
        $streamId: String!,
        $itemPath: [String!]!,
      ) {
        stream(streamId: $streamId) {
          id
          streamId
          labelJSON
          itemHistory(path: $itemPath) {
            edges {
              node {
                id
                valueJSON
                unit
                snapshotId
                snapshotDate
              }
            }
          }
        }
      }
    `
  })
