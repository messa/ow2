import React from 'react'
import Head from 'next/head'
import NavBar from './NavBar'

function Layout({ children, activeItem }) {
  return (
    <div className='Layout'>
      <Head>
        <title>Overwatch monitoring</title>
        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, shrink-to-fit=no" />
        <link href='//fonts.googleapis.com/css?family=Raleway:400,300,600' rel='stylesheet' type='text/css' />
        <link href="//fonts.googleapis.com/css?family=Inconsolata:400,700&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Roboto+Condensed:300,400,700&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Roboto+Slab:300,400,700&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Open+Sans:300,400,600,700,800&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Open+Sans+Condensed:300,700&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=Lato:300,400,700,900&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=PT+Sans:400,700&amp;subset=latin-ext" rel="stylesheet" />
        <link href="//fonts.googleapis.com/css?family=PT+Sans+Narrow:400,700&amp;subset=latin-ext" rel="stylesheet" />
        <link rel='stylesheet' type='text/css' href='/static/css/normalize.css' />
        <link rel='stylesheet' type='text/css' href='/static/css/skeleton.css' />
        <link rel='stylesheet' type='text/css' href='/static/css/overwatch.css' />
      </Head>
      <NavBar activeItem={activeItem} />
      <br />
      {children}
    </div>
  )
}

export default Layout
