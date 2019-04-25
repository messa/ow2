import React from 'react'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Container from '../components/ui/Container'
import Layout from '../components/Layout'
import LabelFromJSON from '../components/util/LabelFromJSON'
import DateTime from '../components/util/DateTime'

class StreamPage extends React.Component {

  static async getInitialProps({ query }) {
    return {
      alertId: query['id'],
    }
  }

  render() {
    const { alertId, alert } = this.props
    return (
      <Layout activeItem='alerts'>
        <Container>
          <h1>Alert <code>{alert.alertId}</code></h1>
          <pre className='debug'>{JSON.stringify(alert, null, 2)}</pre>
        </Container>
      </Layout>
    )
  }

}

export default withData(
  StreamPage,
  {
    variables: ({ query }, { alertId }) => ({
      alertId,
    }),
    query: graphql`
      query  alertQuery(
        $alertId: String!,
      ) {
        alert(alertId: $alertId) {
          id
          alertId
          streamId
          alertType
          itemPath
          firstSnapshotId
          firstSnapshotDate
          lastSnapshotId
          lastSnapshotDate
          lastItemValueJSON
          lastItemUnit
        }
      }
    `
  })
