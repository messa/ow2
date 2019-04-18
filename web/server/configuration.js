import nconf from 'nconf'
import yaml from 'js-yaml'
import fs from 'fs'

const confPath = process.env.OW_WEB_CONF || process.env.CONF;

// if (!confPath) {
//   throw new Error("Path to configuration file must be defined in env CONF or OVERWATCH_WEB_CONF")
// }

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
    'client_token': "hubclienttopsecret",
  }
})

if (process.env.NODE_ENV === 'production') {
  if (nconf.get('session_secret') === 'topsecretstringhere' && !process.env.INSECURE_SESSION_SECRET_OK) {
    throw new Error("You are supposed to change the value of session_secret")
  }
}

export default nconf
