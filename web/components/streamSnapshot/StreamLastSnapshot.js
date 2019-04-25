import React from 'react'
import { createRefetchContainer, graphql } from 'react-relay'
import StreamSnapshot from './StreamSnapshot'

const refetchIntervalMS = 3 * 1000

class StreamLastSnapshot extends React.Component {

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
      ({ streamId, withItems, withJSON }) => ({
        streamId: streamId || this.props.stream.streamId,
        withItems, withJSON
      }),
      null,
      (err) => {
        if (err) {
          console.warn('Refetched with errors:', err)
        }
        this.setState({ refetchCount: this.refetchCount++ })
        this.refetchTimeoutId = setTimeout(this.refetch, refetchIntervalMS)
      },
      { force: true }
    )
  }

  render() {
    const { stream, stateView, nestedViewHref, flatViewHref, jsonViewHref } = this.props
    const { streamId, lastSnapshot } = stream
    if (!lastSnapshot) return null
    return (
      <StreamSnapshot
        key={lastSnapshot.id}
        streamId={streamId}
        snapshot={lastSnapshot}
        stateView={stateView}
        nestedViewHref={nestedViewHref}
        flatViewHref={flatViewHref}
        jsonViewHref={jsonViewHref}
      />
    )
  }

}

export default createRefetchContainer(
  StreamLastSnapshot,
  {
    stream: graphql`
      fragment StreamLastSnapshot_stream on Stream @argumentDefinitions(
        withJSON: { type: "Boolean", defaultValue: false },
        withItems: { type: "Boolean", defaultValue: false },
      ) {
        id
        streamId
        lastSnapshotDate
        lastSnapshot {
          id
          ...StreamSnapshot_snapshot @arguments(
            withJSON: $withJSON,
            withItems: $withItems,
          )
        }
      }
    `
  },
  graphql`
    query StreamLastSnapshotQuery(
      $streamId: String!,
      $withJSON: Boolean!,
      $withItems: Boolean!,
    ) {
      stream(streamId: $streamId) {
        id
        streamId
        lastSnapshotDate
        ...StreamLastSnapshot_stream @arguments(
          withJSON: $withJSON,
          withItems: $withItems,
        )
      }
    }
  `)
