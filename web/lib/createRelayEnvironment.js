import { Environment, Network, RecordSource, Store } from 'relay-runtime'
import fetch from 'isomorphic-unfetch'

let relayEnvironment = null

function getFetchQuery(req) {
  // parameter req is from Next.js getInitialProps (server-only)

  // Define a function that fetches the results of an operation (query/mutation/etc)
  // and returns its results as a Promise
  return async function fetchQuery (operation, variables, cacheConfig, uploadables) {
    const gqlEndpoint = process.browser ? '/graphql' : 'http://127.0.0.1:3000/graphql'
    const fetchOptions = {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      }, // Add authentication and other headers here
      body: JSON.stringify({
        query: operation.text, // GraphQL text from input
        variables
      })
    }
    if (req) {
      // we are in server Node.js (Next.js SSR)
      const gqlEndpoint = req.configuration.get('overwatch_hub:url')
      const hubClientToken = req.configuration.get('overwatch_hub:client_token')
      fetchOptions.headers['Authorization'] = `Bearer ${hubClientToken}`
      fetchOptions.credentials = 'omit'
      const res = await fetch(gqlEndpoint, fetchOptions)
      if (res.status !== 200) {
        const text = await res.text()
        throw new Error(`SSR GQL POST ${gqlEndpoint} status ${res.status}: ${text}`)
      }
      return await res.json()
    } else {
      // we are in browser
      fetchOptions.credentials = 'include'
      const res = await fetch('/graphql', fetchOptions)
      if (res.status !== 200) {
        const text = await res.text()
        throw new Error(`GQL POST ${gqlEndpoint} status ${res.status}: ${text}`)
      }
      return await res.json()
    }

  }
}

export default function initEnvironment ({ req, records = {} }) {
  // Create a network layer from the fetch function
  const network = Network.create(getFetchQuery(req))
  const store = new Store(new RecordSource(records))

  // Make sure to create a new Relay environment for every server-side request so that data
  // isn't shared between connections (which would be bad)
  if (!process.browser) {
    return new Environment({
      network,
      store
    })
  }

  // reuse Relay environment on client-side
  if (!relayEnvironment) {
    relayEnvironment = new Environment({
      network,
      store
    })
  }

  return relayEnvironment
}
