import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import withData from '../lib/withData'

class StreamSnapshotPage extends React.Component {

  render() {
    const { snapshot } = this.props
    const { snapshotId, stream } = snapshot
    const { streamId } = stream
    return (
      <Layout activeItem='streams'>
        <Container>

          <h1>
            Stream
            <Link
              href={{
                pathname: '/stream',
                query: { 'id': streamId, 'tab': 'history' }
              }}
            ><a>
              <code>{streamId}</code>
            </a></Link>
            ▸
            Snapshot <code>{snapshotId}</code>
          </h1>


          <pre>{JSON.stringify(snapshot, null, 2)}</pre>
        </Container>
      </Layout>
    )
  }

}

export default withData(StreamSnapshotPage, {
  variables: ({ query }) => ({
    snapshotId: query.id,
  }),
  query: graphql`
    query streamSnapshotQuery(
      $snapshotId: String!
    ) {
      snapshot: streamSnapshot(snapshotId: $snapshotId) {
        id
        snapshotId
        stream {
          id
          streamId
          labelJSON
        }
      }
    }
  `
})
