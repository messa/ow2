import React from 'react'
import Link from 'next/link'
import { createRefetchContainer, graphql } from 'react-relay'
import DateTime from './util/DateTime'
import LabelFromJSON from './util/LabelFromJSON'
import SnapshotItemValue from '../components/streamSnapshot/SnapshotItemValue'

const refetchIntervalMS = 3 * 1000

class ActiveAlertList extends React.Component {

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
    console.debug('Refetching')
    this.refetchTimeoutId = null
    this.props.relay.refetch(
      {},
      null,
      () => {
        console.debug('Refetched')
        this.setState({ refetchCount: this.refetchCount++ })
        this.refetchTimeoutId = setTimeout(this.refetch, refetchIntervalMS)
      },
      { force: true }
    )
  }

  render() {
    const { query } = this.props
    const { refetchCount } = this.state
    const activeAlerts = query.activeAlerts.edges.map(edge => edge.node)
    return (
      <div className='ActiveAlertList'>
        {activeAlerts.length == 0 ? (
          <p>No alerts :)</p>
        ) : (
          <table className='u-full-width'>
            <thead>
              <tr>
                <th>Alert id</th>
                <th>Stream id</th>
                <th>Stream labels</th>
                <th>Type</th>
                <th>Item</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {activeAlerts.map(alert => (
                <tr key={alert.id}>
                  <td>
                    <code>{alert.alertId}</code>
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
                  <td>
                    <SnapshotItemValue
                      valueJSON={alert.lastItemValueJSON}
                      unit={alert.lastItemUnit}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    )
  }

}

export default createRefetchContainer(
  ActiveAlertList,
  {
    query: graphql`
      fragment ActiveAlertList_query on Query {
        activeAlerts {
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
            }
          }
        }
      }
    `
  },
  graphql`
    query ActiveAlertListQuery {
      ...ActiveAlertList_query
    }
  `)
