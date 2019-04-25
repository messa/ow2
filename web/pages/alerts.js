import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import ActiveAlertList from '../components/alerts/ActiveAlertList'
import InactiveAlertList from '../components/alerts/InactiveAlertList'

class DashboardPage extends React.Component {

  render() {
    return (
      <Layout activeItem='alerts'>
        <Container>
          <h2>Active alerts</h2>
          <ActiveAlertList query={this.props} />

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
        ...ActiveAlertList_query
        ...InactiveAlertList_query
      }
    `
  })
