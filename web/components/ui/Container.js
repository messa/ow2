import React from 'react'

export default ({ children, wide }) => (
  <div className={wide ? 'owContainerWide' : 'owContainer'}>
    {children}
  </div>
)
