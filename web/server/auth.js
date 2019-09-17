import { Router } from 'express'
import passport from 'passport'
import { OAuth2Strategy as GoogleStrategy } from 'passport-google-oauth'
import configuration from './configuration'

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
    if (req.user.provider === 'google') {
      res.cookie(configuration.get('token_cookie_name'), 'google:' + req.user.googleAccessToken)
      return res.redirect('/dashboard')
    }
    res.status(500).send('Unknown req.user provider')
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
        return done(null, {
          provider: 'google',
          googleId: profile.id,
          // displayName: profile.displayName,
          // email: profile.emails[0].value,
          // locale: profile._json.locale,
          // pictureUrl: profile.photos ? profile.photos[0].value : null,
          googleAccessToken: accessToken,
        })
      } catch (err) {
        return done(err, null)
      }
    }
  ))
}
