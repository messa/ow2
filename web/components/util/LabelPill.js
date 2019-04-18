import React from 'react'
import Link from 'next/link'

export default function LabelPill({ label, value, href }) {
  const content = (
    <>
      <b>{label}</b>
      <code>{value}</code>
    </>
  )
  if (href) {
    return (<Link href={href}><a className='LabelPill'>{content}</a></Link>)
  } else {
    return (<span className='LabelPill'>{content}</span>)
  }
}
