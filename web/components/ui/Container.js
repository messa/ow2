import React from 'react'

export default ({ children }) => (
  <div className='owContainer'>
    {children}
    <style jsx>{`
      .owContainer {
        margin-left: 15px;
        margin-right: 15px;
      }
      @media (min-width: 550px) {
        .owContainer {
          margin-left: 20px;
          margin-right: 20px;
        }
      }
      @media (min-width: 1000px) {
        .owContainer {
          width: 100%;
          max-width: 960px;
          margin: 0 auto;
          padding: 0 20px;
        }
      }
    `}</style>
  </div>
)
