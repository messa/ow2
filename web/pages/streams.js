import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import Container from '../components/ui/Container'
import withData from '../lib/withData'
import LabelPill from '../components/util/LabelPill'

function SortLink({ label, activeSortBy, labelFilter }) {
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
    if (labelFilter) {
      href.query['labelFilter'] = JSON.stringify(labelFilter)
    }
    return (
      <Link href={href}><a style={style}>{label}</a></Link>
    )
  }
}

class StreamsPage extends React.Component {

  static async getInitialProps({ query }) {
    const sortBy = query['sortBy'] || 'agent,host'
    const labelFilter = query['labelFilter'] ? JSON.parse(query['labelFilter']) : {}
    if (query['labelKey'] && query['labelValue']) {
      labelFilter[query['labelKey']] = query['labelValue']
    }
    return {
      labelFilter,
      sortBy,
    }
  }

  render() {
    const { labelFilter, sortBy } = this.props
    return (
      <Layout activeItem='streams'>
        <Container wide>
          {labelFilter && Object.keys(labelFilter).length > 0 && (
            <p>
              Filter by label: &nbsp;
              {Object.keys(labelFilter).map((k, n) => (
                <LabelPill
                  key={n}
                  labelKey={k}
                  labelValue={labelFilter[k]}
                  href={false}
                />
              ))}
            </p>
          )}
          <p>
            Sort by:
            <SortLink label='agent, host' activeSortBy={sortBy} labelFilter={labelFilter} />
            <SortLink label='host, agent' activeSortBy={sortBy} labelFilter={labelFilter} />
          </p>
          <StreamList query={this.props} sortBy={sortBy} labelFilter={labelFilter} />
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
