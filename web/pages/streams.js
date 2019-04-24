import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import Container from '../components/ui/Container'
import withData from '../lib/withData'

function SortLink({ label, activeSortBy }) {
  const sortByValue = label.replace(/ /g, '')
  const style = { marginLeft: 8 }
  if (sortByValue === activeSortBy) {
    return (
      <b style={style}>{label}</b>
    )
  } else {
    const href = {
      pathname: '/streams',
      query: { sortBy: sortByValue },
    }
    return (
      <Link href={href}><a style={style}>{label}</a></Link>
    )
  }
}

class StreamsPage extends React.Component {

  static async getInitialProps({ query }) {
    const sortBy = query['sortBy'] || 'agent,host'
    return {
      sortBy,
    }
  }

  render() {
    const { sortBy } = this.props
    return (
      <Layout activeItem='streams'>
        <Container>
          <p>
            Sort by:
            <SortLink label='agent, host' activeSortBy={sortBy} />
            <SortLink label='host, agent' activeSortBy={sortBy} />
          </p>
          <StreamList query={this.props} sortBy={sortBy} />
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
