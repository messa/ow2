import React from 'react'
import SnapshotItemValue from './SnapshotItemValue'

export default class FlatItems extends React.Component {

  render() {
    const { stateItems } = this.props
    return (
      <div className='streamSnapshot-FlatItems'>

        {stateItems && stateItems.map((item, i) => (
          <div key={i} className='flatStateItem' style={{ padding: '1px 6px' }}>

            <span className='path'>
              {item.path.map((pathPart, i) => (
                <span key={i}>
                  {i > 0 && (
                    <span style={{ color: '#666' }}> > </span>
                  )}
                  {i < item.path.length - 1 ? (
                    pathPart
                  ) : (
                    <b className='key'>{pathPart}</b>
                  )}
                </span>
              ))}
            </span>

            {item.valueJSON && (
              <span className='value' style={{ marginLeft: 10 }}>
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

          </div>
        ))}

      </div>
    )
  }

}
