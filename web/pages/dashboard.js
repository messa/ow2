import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import ActiveAlertList from '../components/alerts/ActiveAlertList'

class DashboardPage extends React.Component {

  render() {
    return (
      <Layout activeItem='dashboard'>
        <Container>
          <h2>Active alerts</h2>
          <ActiveAlertList query={this.props} />

          <p>
            <Link href='/alerts'><a>See all alerts</a></Link>
          </p>

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
        ...ActiveAlertList_query
      }
    `
  })
