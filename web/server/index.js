import express from 'express'
import next from 'next'
import bodyParser from 'body-parser'
import setupProxies from './proxies'
import configuration from './configuration'

const port = configuration.get('port') || 3000
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

function transparentFavicon(req, res) {
  const b64 = 'AAABAAEAEBACAAEAAQCwAAAAFgAAACgAAAAQAAAAIAAAAAEAAQAAAAAAgAAA' +
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' +
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//wAA//8AAP//AAD//wAA' +
    '//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA'
  res.set('Content-Type', 'image/x-icon')
  res.send(Buffer.from(b64, 'base64'))
}

app.prepare().then(() => {
  const server = express()

  server.get('/favicon.ico', transparentFavicon)

  server.use(bodyParser.json())

  setupProxies(server)

  server.use((req, res, next) => {
    req.configuration = configuration
    next()
  })

  server.get('*', handle)

  server.listen(port, err => {
    if (err) throw err
    console.log(`> Ready on http://localhost:${port}`)
  })
})
