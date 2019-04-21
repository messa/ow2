import React from 'react'
import { createRefetchContainer, graphql } from 'react-relay'
import Link from 'next/link'
import LabelFromJSON from './util/LabelFromJSON'
import DateTime from './util/DateTime'

const refetchIntervalMS = 3 * 1000

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
    const { relay } = this.props
    relay.refetch(
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
    const { query } = this.props
    const streamNodes = query.streams.edges.map(e => e.node)
    return (
      <div className='StreamList'>
        <table className='u-full-width'>
          <thead>
            <tr>
              <th>Stream Id</th>
              <th>Label</th>
              <th>Last updated</th>
            </tr>
          </thead>
          <tbody>
            {streamNodes.map(stream => (
              <tr key={stream.id}>
                <td>
                  <Link href={{ pathname: '/stream', query: { id: stream.streamId } }}><a>
                    <code>{stream.streamId}</code>
                  </a></Link>
                </td>
                <td>
                  <LabelFromJSON labelJSON={stream.labelJSON} />

                  {' '}&nbsp;{' '}

                  {!stream.lastSnapshot.greenCheckCount || (
                    <span className='greenCheckCount'>{JSON.stringify(stream.lastSnapshot.greenCheckCount)}</span>
                  )}
                  {!stream.lastSnapshot.redCheckCount || (
                    <span className='redCheckCount'>{stream.lastSnapshot.redCheckCount}</span>
                  )}
                </td>

                <td><DateTime key={this.state.refetchCount} value={stream.lastSnapshotDate} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        <style jsx>{`
          .greenCheckCount,
          .redCheckCount {
            margin-left: 4px;
            font-weight: 600;
            color: #fff;
            display: inline-block;
            min-width: 16px;
            text-align: center;
            border-radius: 8px;
          }
          .greenCheckCount {
            background-color: #0c0;
          }
          .redCheckCount {
            background-color: #d00;
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
