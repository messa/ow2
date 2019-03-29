import Head from 'next/head'

export default ({ children }) => (
  <div className='Layout'>
    <Head>
      <title>Overwatch monitoring</title>
      <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, shrink-to-fit=no" />
      <link href='//fonts.googleapis.com/css?family=Raleway:400,300,600' rel='stylesheet' type='text/css' />
      <link rel='stylesheet' type='text/css' href='/static/css/normalize.css' />
      <link rel='stylesheet' type='text/css' href='/static/css/skeleton.css' />
      <link rel='stylesheet' type='text/css' href='/static/css/overwatch.css' />
    </Head>
    <br />
    {children}
  </div>
)
