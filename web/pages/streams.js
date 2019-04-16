import React from 'react'
import { graphql } from 'react-relay'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import Container from '../components/ui/Container'
import withData from '../lib/withData'

class StreamsPage extends React.Component {

  render() {
    return (
      <Layout activeItem='streams'>
        <Container>
          <StreamList query={this.props} />
        </Container>
      </Layout>
    )
  }

}

export default withData(StreamsPage, {
  query: graphql`
    query streamsQuery {
      ...StreamList_query
    }
  `
})
