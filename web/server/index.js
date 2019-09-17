import express from 'express'
import cookieSession from 'cookie-session'
import next from 'next'
import configuration from './configuration'
import { stripSlash } from './util'
import { setupAuth } from './auth'

const port = configuration.get('port') || 3000
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const server = express()

  server.set('trust proxy', 1)

  server.use('/', (req, res, next) => {
    console.info(`* ${req.method} ${req.path}`)
    next()
  })

  server.use(cookieSession({
    name: configuration.get('session_cookie_name'),
    secret: configuration.get('session_secret') || Math.random().toString(36).substring(2),
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  }))

  setupAuth(server, configuration)

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
