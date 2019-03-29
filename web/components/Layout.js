import Head from 'next/head'

export default ({ children }) => (
  <div className='Layout'>
    <Head>
      <title>Overwatch monitoring</title>
      <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, shrink-to-fit=no" />
    </Head>
    <div>
      <br/>
      {children}
    </div>
  </div>
)
