import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import Link from 'next/link'
import NestedItems from './NestedItems'
import FlatItems from './FlatItems'
import StateViewSwitcher from './StateViewSwitcher'

class StreamSnapshot extends React.Component {

  render() {
    const { snapshot } = this.props
    const { nestedViewHref, flatViewHref, jsonViewHref } = this.props
    let { stateView } = this.props
    return (
      <div className='StreamSnapshot'>

        <StateViewSwitcher
          active={stateView}
          nestedViewHref={nestedViewHref}
          flatViewHref={flatViewHref}
          jsonViewHref={jsonViewHref}
        />

        {stateView === 'nested' && (
          <NestedItems
            stateItems={snapshot.stateItems}
          />
        )}

        {stateView === 'flat' && (
          <FlatItems
            stateItems={snapshot.stateItems}
          />
        )}

        {stateView === 'json' && (
          <>
            <p>The raw JSON state received (re-idented):</p>
            <pre
              style={{
                fontSize: 12,
                maxWidth: 800,
                marginLeft: 'auto',
                marginRight: 'auto',
              }}
            >
              {JSON.stringify(
                JSON.parse(snapshot.stateJSON),
                null, 2)}
            </pre>
          </>
        )}
      </div>
    )
  }

}

export default createFragmentContainer(
  StreamSnapshot,
  {
    snapshot: graphql`
      fragment StreamSnapshot_snapshot on StreamSnapshot @argumentDefinitions(
        withJSON: { type: "Boolean", defaultValue: false },
        withItems: { type: "Boolean", defaultValue: false },
      ) {
        id
        snapshotId
        streamId
        date
        stateJSON @include(if: $withJSON)
        stateItems @include(if: $withItems) {
          path
          valueJSON
          checkJSON
          watchdogJSON
        }
      }
    `
  })
