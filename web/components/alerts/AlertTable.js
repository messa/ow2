import React from 'react'
import Link from 'next/link'
import { createFragmentContainer, graphql } from 'react-relay'
import LabelFromJSON from '../util/LabelFromJSON'
import SnapshotItemValue from '../streamSnapshot/SnapshotItemValue'
import DateTime from '../util/DateTime'

class AlertTable extends React.Component {
  render() {
    const { alerts, showEndDate } = this.props
    const alertNodes = alerts && alerts.edges.map(edge => edge.node)
    if (!alertNodes) return null
    if (alertNodes.length === 0) {
      return (<p className='AlertTable'>No alerts :)</p>)
    }
    return (
      <table className='AlertTable u-full-width'>
        <thead>
          <tr>
            <th>Alert id</th>
            <th>Stream id</th>
            <th>Stream labels</th>
            <th>Type</th>
            <th>Item</th>
            <th>Value</th>
            <th>Start date</th>
            {showEndDate && (<th>End date date</th>)}
          </tr>
        </thead>
        <tbody>
          {alertNodes.map(alert => (
            <tr key={alert.id}>
              <td>
                <Link
                  href={{
                    pathname: '/alert',
                    query: {
                      'id': alert.alertId,
                    }
                  }}
                >
                  <a><code>{alert.alertId}</code></a>
                </Link>
              </td>
              <td>
                <Link
                  href={{
                    pathname: '/stream',
                    query: {
                      'id': alert.streamId,
                    }
                  }}
                >
                  <a>
                    <code>{alert.streamId}</code>
                  </a>
                </Link>
              </td>
              <td>
                <LabelFromJSON labelJSON={alert.stream.labelJSON} />
              </td>
              <td>{alert.alertType}</td>
              <td>{alert.itemPath.join(' > ')}</td>
              <td className='snapshotItemValue'>
                <SnapshotItemValue
                  valueJSON={alert.lastItemValueJSON}
                  unit={alert.lastItemUnit}
                />
              </td>
              <td><DateTime value={alert.firstSnapshotDate} /></td>
              {showEndDate && (
                <td><DateTime value={alert.lastSnapshotDate} /></td>
              )}
            </tr>
          ))}
        </tbody>
        <style jsx>{`
          td.snapshotItemValue {
            max-width: 250px;
          }
        `}</style>
      </table>
    )
  }

}

export default createFragmentContainer(
  AlertTable,
  {
    alerts: graphql`
      fragment AlertTable_alerts on AlertConnection {
        edges {
          node {
            id
            alertId
            alertType
            streamId
            stream {
              labelJSON
            }
            itemPath
            lastItemValueJSON
            lastItemUnit
            firstSnapshotDate
            lastSnapshotDate
          }
        }
      }
    `
  }
)
