import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import NestedItems from './NestedItems'
import FlatItems from './FlatItems'
import StateViewSwitcher from './StateViewSwitcher'

function prettyJSON(jsonStr) {
  let parsed
  try {
    parsed = JSON.parse(jsonStr)
  } catch (err) {
    if (window.console && console.debug) {
      console.debug(`prettyJSON JSON.parse failed: ${err}; jsonStr: ${jsonStr}`)
    }
    return jsonStr
  }
  return JSON.stringify(parsed, null, 2)
}

class StreamSnapshot extends React.Component {

  render() {
    const { snapshot } = this.props
    const { nestedViewHref, flatViewHref, jsonViewHref } = this.props
    let { stateView } = this.props
    if (!snapshot) return null
    const { streamId } = snapshot
    return (
      <div className='StreamSnapshot'>

        <div style={{ float: 'right' }}>
          <StateViewSwitcher
            active={stateView}
            nestedViewHref={nestedViewHref}
            flatViewHref={flatViewHref}
            jsonViewHref={jsonViewHref}
          />
        </div>

        {stateView === 'nested' && (
          <NestedItems
            stateItems={snapshot.stateItems}
            streamId={streamId}
          />
        )}

        {stateView === 'flat' && (
          <FlatItems
            stateItems={snapshot.stateItems}
            streamId={streamId}
          />
        )}

        {stateView === 'json' && (
          <>
            <p style={{ marginTop: 0 }}>
              The raw JSON state received (re-idented):
            </p>
            <pre
              style={{
                fontSize: 12,
                maxWidth: 800,
                marginLeft: 'auto',
                marginRight: 'auto',
              }}
            >
              {prettyJSON(snapshot.stateJSON)}
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
          unit
          isCounter
        }
      }
    `
  })
