import React from 'react'
import Link from 'next/link'
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
                  <Link href={{ pathname: '/streamSnapshot', query: { id: snapshot.snapshotId } }}><a>
                    <code>{snapshot.snapshotId}</code>
                  </a></Link>
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
