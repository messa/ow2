import React from 'react'
import Head from 'next/head'
import NavBar from './NavBar'

export default ({ children, activeItem }) => (
  <div className='Layout'>
    <Head>
      <title>Overwatch monitoring</title>
      <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, shrink-to-fit=no" />
      <link href='//fonts.googleapis.com/css?family=Raleway:400,300,600' rel='stylesheet' type='text/css' />
      <link href="//fonts.googleapis.com/css?family=Inconsolata:400,700&amp;subset=latin-ext" rel="stylesheet" />
      <link rel='stylesheet' type='text/css' href='/static/css/normalize.css' />
      <link rel='stylesheet' type='text/css' href='/static/css/skeleton.css' />
      <link rel='stylesheet' type='text/css' href='/static/css/overwatch.css' />
    </Head>
    <NavBar activeItem={activeItem} />
    <br />
    {children}
  </div>
)
