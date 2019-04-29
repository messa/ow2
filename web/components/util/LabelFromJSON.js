import React from 'react'
import LabelPill from './LabelPill'

function toStr(v) {
  return (typeof v === 'string') ? v : JSON.stringify(v)
}

function getSortedLabelKeys(label, sortBy) {
  if (!sortBy) {
    return Object.keys(label)
  }
  if (typeof sortBy === 'string') {
    sortBy = sortBy.split(',')
  }
  const sortedKeys = []
  for (let part of sortBy) {
    if (label[part]) {
      sortedKeys.push(part)
    }
  }
  for (let key of Object.keys(label)) {
    if (!sortedKeys.includes(key)) {
      sortedKeys.push(key)
    }
  }
  return sortedKeys
}

export default class LabelFromJSON extends React.Component {

  render() {
    const { labelJSON, sortBy } = this.props
    const label = JSON.parse(labelJSON)
    const labelKeys = getSortedLabelKeys(label, sortBy)
    return (
      <span className='LabelFromJSON'>
        {labelKeys.map(k => (
          <LabelPill key={k} labelKey={k} labelValue={label[k]} />
        ))}
      </span>
    )
  }

}

/*
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
*/
