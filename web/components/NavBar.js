import React from 'react'
import Link from 'next/link'

export default ({ activeItem }) => {
  const navLink = (name, href, title) => {
    if (name === activeItem) {
      return (<Link href={href}><a className='active'>{title}</a></Link>)
    } else {
      return (<Link href={href}><a>{title}</a></Link>)
    }
  }
  return (
    <nav className='mainNav'>
      <Link href="/dashboard"><a className='siteName'>Overwatch</a></Link>
      {navLink('dashboard', '/dashboard', 'Dashboard')}
      {navLink('streams', '/streams', 'Streams')}
      {navLink('alerts', '/alerts', 'Alerts')}
      <style jsx>{`
        nav {
          background: hsl(216, 50%, 30%);
          color: #fff;
          display: flex;
          min-height: 30px;
          align-items: center;
          padding: 0 1em;
        }
        nav :global(a) {
          color: hsl(216, 100%, 90%);
          text-decoration: none;
        }
        nav :global(a:hover) {
          color: hsl(216, 100%, 100%);
          text-decoration: none;
        }
        nav :global(a.active) {
          color: hsl(216, 50%, 90%);
          font-weight: 600;
        }
        nav :global(a.active:hover) {
          color: #fff;
        }
        nav > :global(*) {
          padding: 5px 10px;
        }
        nav .siteName,
        nav a.siteName {
          color: hsl(216, 100%, 85%);
          font-weight: 600;
          text-decoration: none;
        }
        nav a.siteName:hover {
          color: hsl(216, 100%, 90%);
        }
      `}</style>
    </nav>
  )
}
