import React from 'react'

function buildTree(flatItems) {
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

function NestedItem({ nodeKey, node }) {
  const { item } = node
  return (
    <li className='nestedItem'>
      <b
        style={{
          display: 'inline-block',
          minWidth: 50,
        }}
      >
        {nodeKey}
      </b>

      {item && (
        <>

          {item.valueJSON && (
            <span className='value' style={{ marginLeft: 5 }}>
              <code style={{ fontSize: 12 }}>
                {item.valueJSON}
              </code>
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

      {node.children.size > 0 && (
        <ul className='nestedItems'>
          {Array.from(node.children.entries()).map(([k, v], i) => (
            <NestedItem key={i} nodeKey={k} node={v} />
          ))}
        </ul>
      )}
    </li>
  )
}

export default class NestedItems extends React.Component {

  render() {
    const { stateItems } = this.props
    const nestedItemsRootNode = buildTree(stateItems)
    return (
      <div className='streamSnapshot-NestedItems'>

        <ul className='nestedItems nestedItemsRoot' style={{ marginTop: 0, marginLeft: 10 }}>
          {Array.from(nestedItemsRootNode.children.entries()).map(([k, v], i) => (
            <NestedItem key={i} nodeKey={k} node={v} />
          ))}
        </ul>

        <style jsx>{`
          .nestedItemsRoot :global(li:first-child) {
            margin-top: 0;
          }
        `}</style>

      </div>
    )
  }

}
