import React from 'react'
import Link from 'next/link'

export default function Tabs({ activeKey, items }) {
  const itemComponents = []
  for (const item of items) {
    const active = item.key === activeKey
    if (item.href) {
      itemComponents.push(
        <Link key={item.key} href={item.href}>
          <a className={active ? 'active' : null}>
            {item.title || item.label}
          </a>
        </Link>
      )
    } else {
      itemComponents.push(
        <span
          key={item.key}
          onClick={item.onClick}
          className={active ? 'active' : null}
        >
          {item.title || item.label}
        </span>
      )
    }
  }
  return (
    <div className='Tabs'>
      {itemComponents}
    </div>
  )
}
