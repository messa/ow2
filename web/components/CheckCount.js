import React from 'react'

export default function CheckCount({ color, children }) {
  return (
    <span className={'CheckCount ' + color}>{children}</span>
  )
}
