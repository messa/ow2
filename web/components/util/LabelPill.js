import React from 'react'
import Link from 'next/link'

function LabelPill({ labelKey, labelValue, href }) {
  const content = (
    <>
      <b>{labelKey}</b>
      <code>{labelValue}</code>
    </>
  )
  if (!href && href !== false) {
    href = {
      pathname: '/streams',
      query: {
        'labelKey': labelKey,
        'labelValue': labelValue,
      },
    }
  }
  if (href) {
    return (<Link href={href}><a className='LabelPill'>{content}</a></Link>)
  } else {
    return (<span className='LabelPill'>{content}</span>)
  }
}

export default LabelPill
