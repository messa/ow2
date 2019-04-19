import React from 'react'
import Link from 'next/link'

class StateViewSwitcher extends React.Component {

  render() {
    const { active, nestedViewHref, flatViewHref, jsonViewHref } = this.props
    const choices = [
      {
        key: 'nested',
        title: 'Nested',
        href: nestedViewHref,
      }, {
        key: 'flat',
        title: 'Flat',
        href: flatViewHref,
      }, {
        key: 'json',
        title: 'JSON',
        href: jsonViewHref,
      }
    ]
    return (
      <div className='StateViewSwitcher'>
        {choices.map(ch => (
          ch.key == active ? (
            <b key={ch.key} className='active'>{ch.title}</b>
          ) : (
            <Link key={ch.key} href={ch.href}><a>
              {ch.title}
            </a></Link>
          )
        ))}
        <style jsx>{`
          .StateViewSwitcher {
            margin-top: 16px;
            margin-bottom: 16px;
          }
          .StateViewSwitcher > * {
            padding: 3px 10px;
            border-top: 1px solid #999;
            border-bottom: 1px solid #999;
            border-left: 1px solid #999;
            background-color: hsl(0, 0%, 95%);
          }
          .StateViewSwitcher > :first-child {
            border-radius: 5px 0 0 5px;
          }
          .StateViewSwitcher > :last-child {
            border-right: 1px solid #999;
            border-radius: 0 5px 5px 0;
          }
          .StateViewSwitcher > .active {
            background-color: hsl(0, 0%, 99%);
          }
          .StateViewSwitcher a {
            color: #333;
            text-decoration: none;
          }
        `}</style>
      </div>
    )
  }

}

export default StateViewSwitcher
