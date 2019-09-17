import React from 'react'
import Link from 'next/link'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'

export default () => (
  <Layout>
    <Container>
      <h1>Overwatch monitoring</h1>
      <p>Lorem ipsum dolor sit amet.</p>
      <p><Link href='/login'><a>Login</a></Link></p>
    </Container>
  </Layout>
)
