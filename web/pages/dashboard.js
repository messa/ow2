import React from 'react'
import Link from 'next/link'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'
import LabelFromJSON from '../components/util/LabelFromJSON'
import SnapshotItemValue from '../components/streamSnapshot/SnapshotItemValue'

class DashboardPage extends React.Component {

  render() {
    const activeAlerts = this.props.activeAlerts.edges.map(edge => edge.node)
    return (
      <Layout activeItem='dashboard'>
        <Container>

          <h2>Active alerts</h2>

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
  })
