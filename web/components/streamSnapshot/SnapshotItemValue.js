import React from 'react'

const round = Math.round

function SnapshotItemValue({ item, valueJSON, unit }) {
  if (item && !valueJSON) {
    valueJSON = item.valueJSON
    unit = item.unit
  }
  const value = JSON.parse(valueJSON)
  if (unit === 'bytes' && typeof value === 'number') {
    if (value < 1000) return value + ' B'
    if (value < 1000000) return round(value / 1024) + ' kB'
    if (value < 10000000000) return round(value / (1024 * 1024)) + ' MB'
    return round(value / (1024 * 1024 * 1024)) + ' GB'
  }
  if (unit === 'percents') {
    return value + ' %'
  }
  if (typeof value === 'number') {
    if (round(value) === value) return value
    return round(value * 1000000) / 1000000
  }
  return (
    <code style={{ fontSize: 12, wordBreak: 'break-word' }}>
      {valueJSON}
    </code>
  )
}

export default SnapshotItemValue
