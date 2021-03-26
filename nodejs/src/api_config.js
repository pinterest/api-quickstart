export default class ApiConfig {
  constructor() {
    // Construct the redirect_uri for the OAuth process. The REDIRECT_URI must
    // be literally the same as configured at https://developers.pinterest.com/manage/.
    // The port is fixed for now. It would be better to configure a selection
    // of ports that could be used in case some other service is listening on
    // the hard-coded port.
    const DEFAULT_PORT = 8085;
    const DEFAULT_REDIRECT_URI = 'https://localhost:' + DEFAULT_PORT + '/';
    const DEFAULT_API_URI = 'https://api.pinterest.com';
    const DEFAULT_OAUTH_URI = 'https://www.pinterest.com';
    const DEFAULT_LANDING_URI = 'https://developers.pinterest.com/manage/';
    const DEFAULT_KEY_FILE = 'localhost-key.pem';
    const DEFAULT_CERT_FILE = 'localhost.pem';

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

    this.https_key_file = process.env.HTTPS_KEY_FILE || DEFAULT_KEY_FILE
    this.https_cert_file = process.env.HTTPS_CERT_FILE || DEFAULT_CERT_FILE

    // swizzle oauth and api hosts, based on environment
    this.oauth_uri = process.env.PINTEREST_OAUTH_URI || DEFAULT_OAUTH_URI
    this.api_uri = process.env.PINTEREST_API_URI || DEFAULT_API_URI
  }
}