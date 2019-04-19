import React from 'react'
import DateTime from './util/DateTime'

class SnapshotHistory extends React.Component {

  render() {
    const { snapshots } = this.props
    return (
      <div className='SnapshotHistory'>
        <table>
          <tbody>
            {snapshots.map(snapshot => (
              <tr key={snapshot.id}>
                <td>
                  <code>{snapshot.snapshotId}</code>
                </td>
                <td>
                  <DateTime value={snapshot.date} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

}

export default SnapshotHistory
