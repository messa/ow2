import React from 'react'
import Link from 'next/link'
import { withRouter } from 'next/router'
import { graphql } from 'react-relay'
import withData from '../lib/withData'
import Container from '../components/ui/Container'
import Tabs from '../components/ui/Tabs'
import Layout from '../components/Layout'
import StreamList from '../components/StreamList'
import SnapshotHistory from '../components/SnapshotHistory'
import LabelFromJSON from '../components/util/LabelFromJSON'
import DateTime from '../components/util/DateTime'
import SnapshotItemValue from '../components/streamSnapshot/SnapshotItemValue'

function addValueDelta(records) {
  // assumes that records are sorted from latest
  const out = new Array()
  let prevDateMS = null
  let prevValue = null
  for (let i = records.length - 1; i >= 0; i--) {
    const record = records[i]
    const dateMS = new Date(record.snapshotDate) * 0.001
    const value = JSON.parse(record.valueJSON)
    let valueDelta = null
    if (prevDateMS) {
      if (prevDateMS >= dateMS) {
        throw new Error('Not sorted by date')
      }
      valueDelta = (value - prevValue) / (dateMS - prevDateMS)
    }
    out.push({ ...record, value, valueDelta })
    prevDateMS = dateMS
    prevValue = value
  }
  out.reverse()
  return out
}

function round3(n) {
  return typeof n === 'number' ? Math.round(n * 1000) / 1000 : n
}

class SnapshotItemHistoryPage extends React.Component {

  static async getInitialProps({ query }) {
    const { streamId } = query
    const itemPath = JSON.parse(query['itemPathJSON'])
    return {
      streamId,
      itemPath,
    }
  }

  render() {
    const { streamId, itemPath, stream } = this.props
    const records = stream.itemHistory.edges.map(edge => edge.node)
    const recordsWithDelta = addValueDelta(records)
    const maxValue = recordsWithDelta.map(r => Math.abs(r.value)).filter(n => n).reduce((a, b) => Math.max(a, b), 0)
    const maxDelta = recordsWithDelta.map(r => Math.abs(r.valueDelta)).filter(n => n).reduce((a, b) => Math.max(a, b), 0)
    return (
      <Layout activeItem='streams'>
        <Container>
          <h1>Snapshot item history</h1>

          <p>
            Stream:

            <Link href={{ pathname: '/stream', query: { id: stream.streamId } }}><a>
              <code>{stream.streamId}</code>
            </a></Link>

            &nbsp; &nbsp;

            <LabelFromJSON labelJSON={stream.labelJSON} />
          </p>

          <p>
            Path:
            <code style={{ fontSize: 14 }}>{itemPath.join(' > ')}</code>
          </p>

          <table>
            <thead>
              <tr>
                <th></th>
                <th>Date</th>
                <th>Value</th>
                <th>Delta</th>
                <th>Snapshot id</th>
              </tr>
            </thead>
            <tbody>
              {recordsWithDelta.map((record, i) => {
                const valueWidth = Math.abs(Math.round(25 * record.value / maxValue))
                const deltaWidth = Math.abs(Math.round(25 * record.valueDelta / maxDelta))
                const deltaColor = record.valueDelta > 0 ? '#c01' : '#1c0'
                return (
                  <tr key={record.id}>
                    <td>{i + 1}.</td>
                    <td><DateTime value={record.snapshotDate} /></td>
                    <td>
                      <div
                        style={{
                          borderLeft: `${valueWidth}px solid #03c`,
                          paddingLeft: 6,
                          textAlign: 'right',
                        }}
                      >
                        <SnapshotItemValue item={record} />
                      </div>
                    </td>
                    <td>
                      <div
                        style={{
                          borderLeft: `${deltaWidth}px solid ${deltaColor}`,
                          paddingLeft: 6,
                          textAlign: 'right',
                        }}
                      >
                        {round3(record.valueDelta)}
                      </div>
                    </td>
                    <td>
                      <Link
                        href={{
                          pathname: '/stream',
                          query: {
                            'id': streamId,
                            'tab': 'history',
                            'historySnapshotId': record.snapshotId,
                          },
                        }}
                      ><a>
                        <code>{record.snapshotId}</code>
                      </a></Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

        </Container>
      </Layout>
    )
  }

}

export default withData(
  SnapshotItemHistoryPage,
  {
    variables: ({ query }, { streamId, itemPath }) => ({
      streamId,
      itemPath,
    }),
    query: graphql`
      query snapshotItemHistoryQuery(
        $streamId: String!,
        $itemPath: [String!]!,
      ) {
        stream(streamId: $streamId) {
          id
          streamId
          labelJSON
          itemHistory(path: $itemPath) {
            edges {
              node {
                id
                valueJSON
                unit
                snapshotId
                snapshotDate
              }
            }
          }
        }
      }
    `
  })
