export class ApiConfig {
  constructor() {
    // Construct the redirect_uri for the OAuth process. The REDIRECT_URI must
    // be literally the same as configured at https://developers.pinterest.com/manage/.
    // The port is fixed for now. It would be better to configure a selection
    // of ports that could be used in case some other service is listening on
    // the hard-coded port.
    const DEFAULT_PORT = 8085;
    const DEFAULT_REDIRECT_URI = 'http://localhost:' + DEFAULT_PORT + '/';
    const DEFAULT_API_URI = 'https://api.pinterest.com';
    const DEFAULT_API_VERSION = 'v3'
    const DEFAULT_OAUTH_URI = 'https://www.pinterest.com';
    const DEFAULT_LANDING_URI = 'https://developers.pinterest.com/manage/';
    const DEFAULT_OAUTH_TOKEN_DIR = '.'

    // Get Pinterest application ID and secret from the OS environment.
    // It is best practice not to store credentials in code.
    this.app_id = process.env.PINTEREST_APP_ID;
    this.app_secret = process.env.PINTEREST_APP_SECRET;
    if (!this.app_id || !this.app_secret) {
      throw new Error('PINTEREST_APP_ID and PINTEREST_APP_SECRET must be set in the environment.')
    }

    // might want to get these from the environment in the future
    this.port = DEFAULT_PORT
    this.redirect_uri = DEFAULT_REDIRECT_URI
    this.landing_uri = process.env.REDIRECT_LANDING_URI || DEFAULT_LANDING_URI + this.app_id

    this.oauth_token_dir = process.env.PINTEREST_OAUTH_TOKEN_DIR || DEFAULT_OAUTH_TOKEN_DIR

    // swizzle oauth and api hosts, based on environment
    this.oauth_uri = process.env.PINTEREST_OAUTH_URI || DEFAULT_OAUTH_URI
    this.api_uri = process.env.PINTEREST_API_URI || DEFAULT_API_URI
    this.version = process.env.PINTEREST_API_VERSION || DEFAULT_API_VERSION

    // default level of verbosity, probably should switch to logging
    this.verbosity = 1
  }
}