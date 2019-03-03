import Head from 'next/head'
import { Container } from 'semantic-ui-react'

export default ({ children }) => (
  <div className='Layout'>
    <Head>
      <title>Pyladies Courseware</title>
      <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, shrink-to-fit=no" />
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css" />
    </Head>
    <Container>
      <br/>
      {children}
    </Container>
  </div>
)
