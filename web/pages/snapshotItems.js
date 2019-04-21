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
    let pathQuery = query['path']
    if (!pathQuery && query['pathJSON']) {
      const pathArray = JSON.parse(query['pathJSON'])
      const pathStr = pathArray.join(' > ')
      pathQuery = escapeRegex(pathStr)
    }
    return {
      pathQuery,
    }
  }

  render() {
    const { pathQuery } = this.props
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item search</h1>
          <p>
            Path query:
            <code>{pathQuery}</code>
          </p>
        </Container>
      </Layout>
    )
  }

}

export default withData(
  SnapshotItemsPage,
  {
    variables: ({ query }, { pathQuery }) => ({
      pathQuery
    }),
    query: graphql`
      query snapshotItemsQuery(
        $pathQuery: String!
      ) {
        searchCurrentSnapshotItems(
          pathQuery: $pathQuery
        ) {
          edges {
            node {
              id
              path
              stream {
                id
                labelJSON
              }
              currentValueJSON
            }
          }
        }
      }
    `
