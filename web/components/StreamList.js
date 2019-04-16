import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import LabelFromJSON from './LabelFromJSON'
import DateTime from './util/DateTime'

class StreamList extends React.Component {
  render() {
    const { query } = this.props
    const streamNodes = query.streams.edges.map(e => e.node)
    return (
      <div className='StreamList'>
        <table className='u-full-width'>
          <thead>
            <tr>
              <th>Stream Id</th>
              <th>Label</th>
              <th>Last updated</th>
            </tr>
          </thead>
          <tbody>
            {streamNodes.map(stream => (
              <tr key={stream.streamId}>
                <td><code>{stream.streamId}</code></td>
                <td><LabelFromJSON labelJSON={stream.labelJSON} /></td>
                <td><DateTime value={stream.lastSnapshot.date} /></td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>
    )
  }
}

export default createFragmentContainer(StreamList, {
  query: graphql`
    fragment StreamList_query on Query {
      streams {
        edges {
          node {
            id
            streamId
            labelJSON
            lastSnapshot {
              date
            }
          }
        }
      }
    }
  `
})
