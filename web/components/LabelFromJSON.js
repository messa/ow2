import React from 'react'

function toStr(v) {
  return (typeof v === 'string') ? v : JSON.stringify(v)
}

export default class LabelFromJSON extends React.Component {

  render() {
    const { labelJSON } = this.props
    const label = JSON.parse(labelJSON)
    return (
      <span className='LabelFromJSON'>
        {Object.keys(label).map(k => (
          <span className='labelItem' key={k}>
            <b>{k}:</b> <code>{toStr(label[k])}</code>
          </span>
        ))}
        <style jsx>{`
          .labelItem {
            margin-left: 1em;
          }
          .labelItem:first-child {
            margin-left: 0px;
          }
          .labelItem code {
            margin: 0;
            padding: 0;
            font-size: inherit;
          }
        `}</style>
      </span>
    )
  }

}