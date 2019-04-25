import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import StreamSnapshot from './StreamSnapshot'

class StreamLastSnapshot extends React.Component {

  render() {
    const { streamId, lastSnapshot, stateView, nestedViewHref, flatViewHref, jsonViewHref } = this.props
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

export default createFragmentContainer(
  StreamLastSnapshot,
  {
    lastSnapshot: graphql`
      fragment StreamLastSnapshot_lastSnapshot on StreamSnapshot @argumentDefinitions(
        withJSON: { type: "Boolean", defaultValue: false },
        withItems: { type: "Boolean", defaultValue: false },
      ) {
        id
        ...StreamSnapshot_snapshot @arguments(
          withJSON: $withJSON,
          withItems: $withItems,
        )
      }
    `
  })
