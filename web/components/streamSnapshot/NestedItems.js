import React from 'react'
import FullWidth from '../ui/FullWidth'
import StreamItemDetail from './StreamItemDetail'
import SnapshotItemValue  from './SnapshotItemValue'

function buildTree(flatItems) {
  if (!flatItems) {
    return null
  }
  const root = {
    children: new Map(),
  }
  for (const item of flatItems) {
    let currentNode = root
    for (const part of item.path) {
      if (currentNode.children.has(part)) {
        currentNode = currentNode.children.get(part)
      } else {
        const newNode = {
          children: new Map(),
        }
        currentNode.children.set(part, newNode)
        currentNode = newNode
      }
    }
    currentNode.item = item
  }
  return root
}

class NestedItem extends React.Component {

  state = {
    showDetails: false,
  }

  onValueClick = () => {
    this.setState({ showDetails: !this.state.showDetails })
  }

  render() {
    const { nodeKey, node, streamId } = this.props
    const { item } = node
    const { showDetails } = this.state
    return (
      <li className='nestedItem'>

        <div className='itemData'>
          <b
            style={{
              display: 'inline-block',
              minWidth: 60,
            }}
          >
            {nodeKey}
          </b>

          {item && (
            <>

              {item.valueJSON && (
                <span
                  className='value'
                  style={{
                    marginLeft: 5,
                    cursor: 'pointer',
                    display: 'inline-block',
                    minWidth: 40,
                  }}
                  onClick={this.onValueClick}
                >
                  <SnapshotItemValue item={item} />
                </span>
              )}

              {item.checkJSON && (
                <span className='check' style={{ marginLeft: 10 }}>
                  <b>Check:</b> <code>{item.checkJSON}</code>
                </span>
              )}

              {item.watchdogJSON && (
                <span className='check' style={{ marginLeft: 10 }}>
                  <b>Watchdog:</b> <code>{item.watchdogJSON}</code>
                </span>
              )}

            </>
          )}
        </div>

        {(showDetails || (null && item && item.valueJSON === '4')) && (
          <div style={{ marginTop: 2, marginBottom: 2 }}>
            <FullWidth>
              <StreamItemDetail item={item} streamId={streamId} />
            </FullWidth>
          </div>
        )}

        {node.children.size > 0 && (
          <ul className='nestedItems'>
            {Array.from(node.children.entries()).map(([k, v], i) => (
              <NestedItem key={i} nodeKey={k} node={v} streamId={streamId} />
            ))}
          </ul>
        )}

        <style jsx>{`
          .itemDetails {
            padding: 1px;
            background-color: #eee;
            position: absolute;
            margin-left: calc(-50vw + 50%);
            width: 100vw;
            box-sizing: border-box;
          }
        `}</style>
      </li>
    )
  }

}

export default class NestedItems extends React.Component {

  render() {
    const { stateItems, streamId } = this.props
    const nestedItemsRootNode = buildTree(stateItems)
    if (!nestedItemsRootNode) return null
    return (
      <div className='streamSnapshot-NestedItems'>

        <ul className='nestedItems nestedItemsRoot' style={{ marginTop: 0, marginLeft: 10 }}>
          {Array.from(nestedItemsRootNode.children.entries()).map(([k, v], i) => (
            <NestedItem key={i} nodeKey={k} node={v} streamId={streamId} />
          ))}
        </ul>

        <style jsx>{`
          ul.nestedItemsRoot,
          ul.nestedItemsRoot :global(ul) {
            list-style: circle;
          }
          .nestedItemsRoot :global(li:first-child) {
            margin-top: 0;
          }
        `}</style>

      </div>
    )
  }

}
