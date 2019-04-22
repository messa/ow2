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

const escapeRegex = v => v // TODO :)

class SnapshotItemsPage extends React.Component {

  state = {
    queryValue: null
  }

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

  onQueryChange = ({ target: { value } }) => {
    this.setState({ queryValue: value })
  }

  render() {
    const { itemPathQuery } = this.props
    const { queryValue } = this.state
    const foundItems = this.props.foundItems.edges.map(edge => edge.node)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item search</h1>

          <form className='pathQueryForm'>
            <label>Path query:</label>
            <input
              className="u-full-width"
              name='itemPath'
              value={queryValue !== null ? queryValue : itemPathQuery}
              onChange={this.onQueryChange}
            />
          </form>

          <table className='u-full-width'>
            <thead>
              <tr>
                <th>Stream id</th>
                <th>Stream label</th>
                <th>Path</th>
                <th>Value</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {foundItems.map(item => (
                <tr key={item.id}>
                  <td>
                    <Link href={{ pathname: '/stream', query: { id: item.stream.streamId } }}><a>
                      <code>{item.stream.streamId}</code>
                    </a></Link>
                  </td>
                  <td><LabelFromJSON labelJSON={item.stream.labelJSON} /></td>
                  <td>{item.path.join(' > ')}</td>
                  <td><SnapshotItemValue item={item} /></td>
                  <td><DateTime value={item.snapshotDate} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Container>

        <style jsx>{`
          .pathQueryForm {
            display: flex;
          }
          .pathQueryForm label {
            flex-shrink: 0;
          }
          .pathQueryForm input {
            margin-left: 1em;
            font-size: 14px;
            border-top: none;
            border-right: none;
            border-left: none;
            border-bottom: 1px solid #999;
            outline: none;
          }
        `}</style>

      </Layout>
    )
  }

}

export default withData(
  SnapshotItemsPage,
  {
    variables: ({ query }, { itemPathQuery }) => ({
      itemPathQuery,
    }),
    query: graphql`
      query snapshotItemsQuery(
        $itemPathQuery: String!,
      ) {
        foundItems: searchCurrentSnapshotItems(
          pathQuery: $itemPathQuery
        ) {
          edges {
            node {
              id
              path
              valueJSON
              unit
              snapshotId
              snapshotDate
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
