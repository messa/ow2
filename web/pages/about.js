import React from 'react'
//import { graphql } from 'react-relay'
//import withData from '../lib/withData'
import Layout from '../components/Layout'
import Container from '../components/ui/Container'

class AboutPage extends React.Component {

  render() {
    return (
      <Layout activeItem='about'>
        <Container>
          <h2>About</h2>
        </Container>
      </Layout>
    )
  }

}

export default AboutPage

/*
export default withData(
  AboutPage,
  {
    query: graphql`
      query aboutQuery {
      }
    `
  })
*/
