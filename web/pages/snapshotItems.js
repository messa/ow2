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

const escapeRegex = v => v // TODO :)

class SnapshotItemsPage extends React.Component {

  static async getInitialProps({ query }) {
    let itemPathQuery = query['itemPath']
    if (!itemPathQuery && query['itemPathJSON']) {
      const pathArray = JSON.parse(query['itemPathJSON'])
      const pathStr = pathArray.join(' > ')
      itemPathQuery = escapeRegex(pathStr)
    }
    return {
      itemPathQuery,
    }
  }

  render() {
    const { itemPathQuery, foundItems } = this.props
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item search</h1>
          <p>
            Path query:
            <code>{itemPathQuery}</code>
          </p>

          <pre>{JSON.stringify({ foundItems }, null, 2)}</pre>

        </Container>
      </Layout>
    )
  }

}

export default withData(
  SnapshotItemsPage,
  {
    variables: ({ query }, { itemPathQuery }) => ({
      itemPathQuery
    }),
    query: graphql`
      query snapshotItemsQuery(
        $itemPathQuery: String!
      ) {
        foundItems: searchCurrentSnapshotItems(
          pathQuery: $itemPathQuery
        ) {
          edges {
            node {
              id
              path
              valueJSON
              snapshotId
              stream {
                id
                streamId
                labelJSON
              }
            }
          }
        }
      }
    `
  })
