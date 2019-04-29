import React from 'react'
import Link from 'next/link'
import { createRefetchContainer, graphql } from 'react-relay'
import DateTime from './util/DateTime'
import LabelFromJSON from './util/LabelFromJSON'
import CheckCount from './CheckCount'

const refetchIntervalMS = 3 * 1000

function sortStreams(streamNodes, sortBy) {
  const sortParts = sortBy.split(',')
  streamNodes.sort((a, b) => {
    const aLabel = a.label
    const bLabel = b.label
    for (let part of sortParts) {
      if (aLabel[part] && !bLabel[part]) return -1
      if (!aLabel[part] && bLabel[part]) return 1
      if (aLabel[part] < bLabel[part]) return -1
      if (aLabel[part] > bLabel[part]) return 1
    }
    if (a['labelJSON'] < b['labelJSON']) return -1
    if (a['labelJSON'] > b['labelJSON']) return 1
    return 0
  })
}

class StreamList extends React.Component {

  state = {
    refetchCount: null,
  }

  componentDidMount() {
    this.refetchTimeoutId = setTimeout(this.refetch, refetchIntervalMS)
    this.refetchCount = 0
  }

  componentWillUnmount() {
    if (this.refetchTimeoutId) {
      clearTimeout(this.refetchTimeoutId)
    }
  }

  refetch = () => {
    this.refetchTimeoutId = null
    this.props.relay.refetch(
      {},
      null,
      () => {
        this.setState({ refetchCount: this.refetchCount++ })
        this.refetchTimeoutId = setTimeout(this.refetch, refetchIntervalMS)
      },
      { force: true }
    )
  }

  render() {
    const { query, labelFilter, sortBy } = this.props
    let streamNodes = query.streams && query.streams.edges.map(e => e.node)
    if (!streamNodes) return null
    streamNodes = streamNodes.map(n => ({ label: JSON.parse(n.labelJSON), ...n }))
    if (labelFilter) {
      for (const k of Object.keys(labelFilter)) {
        const v = labelFilter[k]
        streamNodes = streamNodes.filter(node => node.label[k] === v)
      }
    }
    sortStreams(streamNodes, sortBy)
    return (
      <div className='StreamList'>
        <table className='u-full-width'>
          <thead>
            <tr>
              <th>Stream Id</th>
              <th>Label</th>
              <th>Checks</th>
              <th className='lastUpdatedCol'>Last updated</th>
            </tr>
          </thead>
          <tbody>
            {streamNodes && streamNodes.map(stream => (
              <tr key={stream.id}>
                <td>
                  <Link href={{ pathname: '/stream', query: { id: stream.streamId } }}><a>
                    <code>{stream.streamId}</code>
                  </a></Link>
                </td>
                <td>
                  <LabelFromJSON labelJSON={stream.labelJSON} sortBy={sortBy} />
                </td>
                <td>
                  {!stream.lastSnapshot.greenCheckCount || (
                    <CheckCount color='green'>{stream.lastSnapshot.greenCheckCount}</CheckCount>
                  )}
                  {!stream.lastSnapshot.redCheckCount || (
                    <CheckCount color='red'>{stream.lastSnapshot.redCheckCount}</CheckCount>
                  )}
                </td>
                <td className='lastUpdatedCol'><DateTime key={this.state.refetchCount} value={stream.lastSnapshotDate} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        <style jsx>{`
          @media (max-width: 1000px) {
            .StreamList table .lastUpdatedCol {
              display: none;
            }
          }
        `}</style>
      </div>
    )
  }

}

export default createRefetchContainer(
  StreamList,
  {
    query: graphql`
      fragment StreamList_query on Query {
        streams {
          edges {
            node {
              id
              streamId
              labelJSON
              lastSnapshotDate
              lastSnapshot {
                greenCheckCount
                redCheckCount
              }
            }
          }
        }
      }
    `
  },
  graphql`
    query StreamListQuery {
      ...StreamList_query
    }
  `)
