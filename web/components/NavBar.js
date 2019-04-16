import React from 'react'
import Link from 'next/link'

export default ({ activeItem }) => {
  const navLink = (name, href, title) => {
    if (name === activeItem) {
      return (<b><Link href={href}><a className='active'>{title}</a></Link></b>)
    } else {
      return (<Link href={href}><a>{title}</a></Link>)
    }
  }
  return (
    <nav className='mainNav'>
      <div className='siteName'>
        <Link href="/dashboard"><a>Overwatch</a></Link>
      </div>
      {navLink('dashboard', '/dashboard', 'Dashboard')}
      {navLink('streams', '/streams', 'Streams')}
      <style jsx>{`
        nav {
          background: #247;
          color: #fff;
          display: flex;
          min-height: 40px;
          align-items: center;
          padding: 0 1em;
        }
        nav :global(a), nav :global(a.active:hover) {
          color: #fff;
          text-decoration: none;
        }
        nav :global(a:hover) {
          color: #ccc;
          text-decoration: none;
        }
        nav > :global(*) {
          padding: 3px 10px;
        }
        .siteName {
          font-weight: 600;
        }
        .siteName a {
          text-decoration: none;
          color: #acf;
        }
      `}</style>
    </nav>
  )
}
