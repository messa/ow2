import fetch from 'node-fetch'

export function gqlGetProxy(hubGraphQLEndpoint) {
  return async (req, res) => {
    try {
      const fetchOptions = {
        headers: {
          'User-Agent': req.get('User-Agent'),
        }
      }
      const fetchRes = await fetch(hubGraphQLEndpoint, fetchOptions)
      const blob = await fetchRes.arrayBuffer()
      res.status(200)
      res.set({
        'Content-Type': fetchRes.headers.get('Content-Type'),
      })
      res.send(new Buffer(blob))
    } catch (err) {
      console.error(err)
      res.status(500).send('Proxy error')
    }
  }
}

export function gqlPostProxy(hubGraphQLEndpoint) {
  return async (req, res) => {
    try {
      const fetchOptions = {
        method: 'POST',
        body: JSON.stringify(req.body),
        headers: {
          'Content-Type': req.get('Content-Type'),
        }
      }
      const fetchRes = await fetch(hubGraphQLEndpoint, fetchOptions)
      const blob = await fetchRes.arrayBuffer()
      res.status(200)
      res.set({
        'Content-Type': fetchRes.headers.get('Content-Type'),
      })
      res.send(new Buffer(blob))
    } catch (err) {
      console.error(err)
      res.status(500).send('Proxy error')
    }
  }
}
