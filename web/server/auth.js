import { Router } from 'express'
import passport from 'passport'
import { OAuth2Strategy as GoogleStrategy } from 'passport-google-oauth'
import fetch from 'node-fetch'
import configuration from './configuration'
import { stripSlash } from './util'

const hubUrl = stripSlash(configuration.get('overwatch_hub:url'))
const hubGQLEndpoint = hubUrl + '/graphql'

const authRouter = Router()

authRouter.use(passport.initialize())
//authRouter.use(passport.session())

authRouter.get(
  '/auth/google/login',
  passport.authenticate('google')
)

authRouter.get(
  '/auth/google/callback',
  passport.authenticate('google', {
    failureRedirect: '/login?failed=1',
    session: false,
  }),
  function(req, res) {
    if (!req.user) return res.redirect('/login')
    if (req.setHubTokenCookie) {
      res.cookie(req.setHubTokenCookie.name, req.setHubTokenCookie.value)
    }
    return res.redirect('/dashboard')
  }
)

passport.serializeUser((user, done) => done(null, user))
passport.deserializeUser((user, done) => done(null, user))

export function setupAuth(server, configuration) {
  server.use(authRouter)
  setupGoogle(configuration)
}

function setupGoogle(configuration) {
  if (!configuration.get('google_oauth2:client_id')) return
  if (!configuration.get('google_oauth2:client_secret')) return
  passport.use(new GoogleStrategy(
    {
      clientID: configuration.get('google_oauth2:client_id'),
      clientSecret: configuration.get('google_oauth2:client_secret'),
      callbackURL: configuration.get('google_oauth2:redirect_url'),
      hd: configuration.get('google_oauth2:hosted_domain'),
      scope: [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
      ],
      prompt: 'select_account',
      state: true,
      passReqToCallback: true,
    },
    async function (req, accessToken, refreshToken, profile, done) {
      try {
        console.debug('Google profile:', JSON.stringify(profile))
        if (!profile.emails || !profile.emails[0]) {
          throw new Error('Did not receive any e-mail in Google profile')
        }
        if (!profile.emails[0].verified) {
          throw new Error(
            'E-mail received in Google profile is not verified: ' +
            JSON.stringify(profile.emails))
        }

        const fetchOptions = {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: `
              mutation(
                $googleAccessToken: String!
              ) {
                loginViaGoogleOAuth2Token(
                  googleAccessToken: $googleAccessToken
                ) {
                  errorMessage
                  user {
                    id
                    displayName
                    emailAddress
                  }
                  accessToken
                  accessTokenCookieName
                }
              }
            `,
            variables: {
              googleAccessToken: accessToken,
            }
          })
        }
        const fetchRes = await fetch(hubGQLEndpoint, fetchOptions)
        const fetchResData = await fetchRes.json()
        console.debug(`fetchResData: ${JSON.stringify(fetchResData)}`)
        const { errors, data } = fetchResData
        if (errors) {
          return done(new Error(`GraphQL errors: ${JSON.stringify(errors)}`), null)
        }
        const { errorMessage, user } = data.loginViaGoogleOAuth2Token
        const hubToken = data.loginViaGoogleOAuth2Token.accessToken
        const hubTokenCookieName = data.loginViaGoogleOAuth2Token.accessTokenCookieName

        if (user && hubToken && hubTokenCookieName) {
          req.setHubTokenCookie = {
            name: hubTokenCookieName,
            value: hubToken,
          }
          return done(null, user)
        } else {
          return done(new Error(errorMessage || 'error'), null)
        }
      } catch (err) {
        return done(err, null)
      }
    }
  ))
}
