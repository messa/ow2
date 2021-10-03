import React from 'react'

function CheckCount({ color, children }) {
  return (
    <span className={'CheckCount ' + color}>{children}</span>
  )
}

export default CheckCount
