import express from 'express'
import next from 'next'
import bodyParser from 'body-parser'
import configuration from './configuration'
import { stripSlash } from './util'

const port = configuration.get('port') || 3000
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const server = express()

  server.use('/', (req, res, next) => {
    console.info(`* ${req.method} ${req.path}`)
    next()
  })

  server.get('/', (req, res) => res.redirect('/dashboard'))

  server.use((req, res, next) => {
    req.configuration = configuration
    req.hubGQLEndpoint = stripSlash(configuration.get('overwatch_hub:url')) + '/graphql'
    next()
  })

  server.all('*', handle)

  server.listen(port, err => {
    if (err) throw err
    console.log(`> Ready on http://localhost:${port}`)
  })
})
