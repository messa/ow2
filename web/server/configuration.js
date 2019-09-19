import nconf from 'nconf'
import yaml from 'js-yaml'
import fs from 'fs'

const confPath = process.env.OW_WEB_CONF || process.env.CONF;

if (confPath) {
  if (!fs.existsSync(confPath)) {
    throw new Error(`Configuration file does not exist: ${confPath}`)
  }
  console.debug(`Loading configuration from ${confPath}`)
  nconf.file({
    file: confPath,
    format: {
      parse: (obj, options) => yaml.safeLoad(obj),
      stringify: (obj, options) => yaml.safeDump(obj),
    }
  })
}

nconf.defaults({
  'port': parseInt(process.env.PORT, 10) || 8486,
  'overwatch_hub': {
    'url': 'http://127.0.0.1:8485',
  },
  'google_oauth2': {
    'client_id': null,
    'client_secret': null,
    'redirect_url': null,
    'hosted_domain': null,
    'allowed_emails': null,
  },
  'session_secret': null,
  'session_cookie_name': 'ow2websess',
  'hub_access_token_cookie_name': 'ow2hubtoken',
})

export default nconf
