import React from 'react'
import { graphql } from 'react-relay'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import withData from '../lib/withData'

class StreamsPage extends React.Component {

  render() {
    const { streams } = this.props
    return (
      <Layout activeItem='streams'>
        <Container>
          <pre>{JSON.stringify({ streams }, null, 2)}</pre>
        </Container>
      </Layout>
    )
  }

}

export default withData(StreamsPage, {
  query: graphql`
    query streamsQuery {
      streams {
        edges {
          node {
            streamId
            labelJSON
            lastSnapshot {
              snapshotId
            }
          }
        }
      }
    }
  `
})
