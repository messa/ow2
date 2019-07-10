import React from 'react'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import ActiveUnacknowledgedAlertList from '../components/alerts/ActiveUnacknowledgedAlertList'

class DashboardPage extends React.Component {

  render() {
    return (
      <Layout activeItem='dashboard'>
        <Container wide>
          <h2>Active unacknowledged alerts</h2>
          <ActiveUnacknowledgedAlertList query={this.props} />
        </Container>
      </Layout>
    )
  }

}

export default withData(
  DashboardPage,
  {
    query: graphql`
      query dashboardQuery {
        ...ActiveUnacknowledgedAlertList_query
      }
    `
  })
