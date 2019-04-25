import React from 'react'
import Link from 'next/link'
import { createRefetchContainer, graphql } from 'react-relay'
import AlertTable from './AlertTable'

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
    this.refetchTimeoutId = null
    this.props.relay.refetch(
      {},
      null,
      (err) => {
        if (err) console.warn('Refetch error:', err)
        this.setState({ refetchCount: this.refetchCount++ })
        this.refetchTimeoutId = setTimeout(this.refetch, refetchIntervalMS)
      },
      { force: true }
    )
  }

  render() {
    const { query } = this.props
    const { activeAlerts } = query
    const { refetchCount } = this.state
    return (
      <div className='ActiveAlertList'>
        <AlertTable alerts={activeAlerts} />
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
          ...AlertTable_alerts
        }
      }
    `
  },
  graphql`
    query ActiveAlertListQuery {
      ...ActiveAlertList_query
    }
  `)
