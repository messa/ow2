import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import ActiveAcknowledgedAlertList from '../components/alerts/ActiveAcknowledgedAlertList'
import ActiveUnacknowledgedAlertList from '../components/alerts/ActiveUnacknowledgedAlertList'
import InactiveAlertList from '../components/alerts/InactiveAlertList'

class DashboardPage extends React.Component {

  render() {
    return (
      <Layout activeItem='alerts'>
        <Container wide>
          <h2>Active unacknowledged alerts</h2>
          <ActiveUnacknowledgedAlertList query={this.props} />

          <h2>Active acknowledged alerts</h2>
          <ActiveAcknowledgedAlertList query={this.props} />

          <h2>Inactive alerts</h2>
          <InactiveAlertList query={this.props} />

        </Container>
      </Layout>
    )
  }

}

export default withData(
  DashboardPage,
  {
    query: graphql`
      query alertsQuery {
        ...ActiveAcknowledgedAlertList_query
        ...ActiveUnacknowledgedAlertList_query
        ...InactiveAlertList_query
      }
    `
  })
