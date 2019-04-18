import React from 'react'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import Container from '../components/ui/Container'
import LabelFromJSON from '../components/util/LabelFromJSON'
import DateTime from '../components/util/DateTime'

class StreamsPage extends React.Component {

  render() {
    const { stream } = this.props
    const { lastSnapshot } = stream
    const state = JSON.parse(lastSnapshot.stateJSON)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Stream <code>{stream.streamId}</code></h1>

          <div class="row">
            <div class="eight columns">
              <LabelFromJSON labelJSON={stream.labelJSON} />
            </div>
            <div class="four columns text-right">
              <DateTime value={lastSnapshot.date} />
            </div>
           </div>

           <pre>{JSON.stringify({ state }, null, 4)}</pre>
        </Container>
      </Layout>
    )
  }

}

export default withData(StreamsPage, {
  variables: ({ query }) => ({ streamId: query.id }),
  query: graphql`
    query streamQuery($streamId: String!) {
      stream(streamId: $streamId) {
        id
        streamId
        labelJSON
        lastSnapshot {
          date
          stateJSON
        }
      }
    }
  `
})
