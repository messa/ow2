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
import SnapshotItemValue from '../components/streamSnapshot/SnapshotItemValue'


class SnapshotItemGraphPage extends React.Component {

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
    // const records = stream.itemHistory.edges.map(edge => edge.node)
    // const recordsWithDelta = addValueDelta(records)
    // const maxValue = recordsWithDelta.map(r => Math.abs(r.value)).filter(n => n).reduce((a, b) => Math.max(a, b), 0)
    // const maxDelta = recordsWithDelta.map(r => Math.abs(r.valueDelta)).filter(n => n).reduce((a, b) => Math.max(a, b), 0)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item graph</h1>

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


        </Container>
      </Layout>
    )
  }

}

export default withData(
  SnapshotItemGraphPage,
  {
    variables: ({ query }, { streamId, itemPath }) => ({
      streamId,
      itemPath,
    }),
    query: graphql`
      query snapshotItemGraphQuery(
        $streamId: String!,
      ) {
        stream(streamId: $streamId) {
          id
          streamId
          labelJSON
        }
      }
    `
  })
