import React from 'react'

export default ({ children }) => (
  <div className='owContainer'>
    {children}
    <style jsx>{`
      .owContainer {
        margin-left: 16px;
        margin-right: 16px;
      }
    `}</style>
  </div>
)
