import React from 'react'

function Container({ children, wide }) {
  return (
    <div className={wide ? 'owContainerWide' : 'owContainer'}>
      {children}
    </div>
  )
}

export default Container
