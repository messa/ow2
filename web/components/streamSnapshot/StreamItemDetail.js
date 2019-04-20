import React from 'react'
import Link from 'next/link'

function postprocessJSON(json) {
  json = json.replace(/,"/g, ', "')
  json = json.replace(/([^\\])":/g, '$1": ')
  return json
}

class StreamItemDetail extends React.Component {

  render() {
    const { item, streamId } = this.props
    const historyHref = {
      pathname: '/snapshotItemHistory',
      query: {
        'streamId': streamId,
        'itemPathJSON': JSON.stringify(item.path),
      }
    }
    const searchAllHref = {
      pathname: '/snapshotItems',
      query: {
        'itemPathJSON': JSON.stringify(item.path),
      }
    }
    return (
      <div className='StreamItemDetail'>
        <div className='StreamItemDetail-container'>
          <p className='path'>
            {item.path.map((part, i) => (
              <span key={i}>
                {i > 0 && ' > '}
                <code>{part}</code>
              </span>
            ))}
          </p>

          <p>
            GraphQL item raw data:
            <code>{postprocessJSON(JSON.stringify(item))}</code>
          </p>

          <p>

            <Link href={historyHref}><a className='owButton'>
              History
            </a></Link>

            <Link href={searchAllHref}><a className='owButton'>
              Search all streams
            </a></Link>

          </p>
        </div>
        <style jsx>{`
          .StreamItemDetail {
            padding: 8px 25px;
            background-color: #fcfdfe;
            border-top: 1px dotted #ccc;
            border-bottom: 1px dotted #ccc;
          }
          .StreamItemDetail-container {
            max-width: 900px;
            margin: 0 auto;
          }
          .StreamItemDetail :global(:first-child) {
            margin-top: 0 !important;
          }
          .StreamItemDetail :global(:last-child) {
            margin-bottom: 0 !important;
          }
          .StreamItemDetail .path {
            font-size: 12px;
            font-weight: 300;
            margin-top: 0;
            color: #666;
          }
          .StreamItemDetail .path span:first-child code:first-child {
            padding-left: 0;
          }
          .StreamItemDetail .path b,
          .StreamItemDetail .path code {
            font-weight: 500;
          }
          .StreamItemDetail p,
          .StreamItemDetail pre {
            margin-top: 0.8rem;
            margin-bottom: 0.8rem;
          }
          .StreamItemDetail code {
            white-space: pre-wrap;
          }
          .StreamItemDetail a.owButton {
            border: 1px solid hsl(0, 50%, 50%);
            color: hsl(0, 50%, 50%);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 600;
            background-color: #fff;
            margin-left: 1em;
            text-decoration: none;
          }
          .StreamItemDetail a.owButton:hover {
            text-decoration: none;
          }
          .StreamItemDetail a.owButton:first-child {
            margin-left: 0;
          }

        `}</style>
      </div>
    )
  }

}

export default StreamItemDetail
