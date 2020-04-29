import { Environment, Network, RecordSource, Store } from 'relay-runtime'
import fetch from 'isomorphic-unfetch'

let relayEnvironment = null

function getServerAddress(req) {
  if (!req) return ''
  const port = req.socket.localPort
  if (!port) throw new Error('No req.socket.localPort')
  return `http://localhost:${port}`
}

function getFetchQuery(req) {
  // parameter req is from Next.js getInitialProps (server-only)

  // Define a function that fetches the results of an operation (query/mutation/etc)
  // and returns its results as a Promise
  return async function fetchQuery (operation, variables, cacheConfig, uploadables) {
    const fetchOptions = {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      }, // Add authentication and other headers here
      body: JSON.stringify({
        query: operation.text, // GraphQL text from input
        variables
      }),
      credentials: 'include'
    }
    if (req && req.headers['cookie']) {
      fetchOptions.headers['Cookie'] = req.headers['cookie']
    }
    const gqlEndpoint = req ? req.hubGQLEndpoint : getServerAddress(req) + '/api/graphql'
    const res = await fetch(gqlEndpoint, fetchOptions)
    if (res.status !== 200) {
      const text = await res.text()
      throw new Error(`GQL POST ${gqlEndpoint} status ${res.status}: ${text}`)
    }
    return await res.json()
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
