import React from 'react'
import Link from 'next/link'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'

class LoginPage extends React.Component {


  render() {
    return (
      <Layout>
        <Container>
          <h1>Login</h1>
          <p><a href='/auth/google/login'>Login using google</a></p>
        </Container>
      </Layout>
    )
  }

}

export default LoginPage
