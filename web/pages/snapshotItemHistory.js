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
import StreamSnapshot from '../components/streamSnapshot/StreamSnapshot'

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
            Stream: <code>{streamId}</code>
          </p>

          <p>
            Path:
            <code>{itemPath.join(' > ')}</code>
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
                  <td><code>{record.valueJSON}</code></td>
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
                snapshotId
                snapshotDate
              }
            }
          }
        }
      }
    `
  })
