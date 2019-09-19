import fetch from 'node-fetch'
import configuration from '../../server/configuration'
import { asyncWrapper, stripSlash } from '../../server/util'

const hubUrl = stripSlash(configuration.get('overwatch_hub:url'))

const tokenCookieName = configuration.get('hub_access_token_cookie_name')

export default asyncWrapper(async (req, res) => {
  console.info(`Processing ${req.method} ${req.url}`)
  const fetchOptions = {
    method: req.method,
    headers: {
      'Accept': req.headers['accept'],
      'User-Agent': req.headers['user-agent'],
      'Content-Type': req.headers['content-type'],
    }
  }
  if (req.cookies[tokenCookieName]) {
    console.debug('XXX cookie:', req.cookies[tokenCookieName])
    fetchOptions.headers['Cookie'] = `${tokenCookieName}=${encodeURIComponent(req.cookies[tokenCookieName])}`
  }
  if (req.body) {
    fetchOptions.body = JSON.stringify(req.body)
  }
  const hubGQLEndpoint = hubUrl + '/graphql'
  const fetchRes = await fetch(hubGQLEndpoint, fetchOptions)
  const blob = await fetchRes.arrayBuffer()
  res.status(fetchRes.status)
  res.setHeader('Content-Type', fetchRes.headers.get('Content-Type'))
  res.end(Buffer.from(blob))
})
