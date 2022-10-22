import process from 'process';
import { bootstrap } from 'global-agent';

export class ApiConfig {
  constructor({ verbosity = 2 }) {
    // Construct the redirect_uri for the OAuth process. The REDIRECT_URI must
    // be literally the same as configured at https://developers.pinterest.com/apps/.
    // The port is fixed for now. It would be better to configure a selection
    // of ports that could be used in case some other service is listening on
    // the hard-coded port.
    const DEFAULT_PORT = 8085;
    const DEFAULT_REDIRECT_URI = `http://localhost:${DEFAULT_PORT}/`;
    const DEFAULT_API_URI = 'https://api.pinterest.com';
    const DEFAULT_OAUTH_URI = 'https://www.pinterest.com';
    const DEFAULT_LANDING_URI = 'https://developers.pinterest.com/apps/';
    const DEFAULT_OAUTH_TOKEN_DIR = '.';

    // default level of verbosity, probably should switch to logging
    this.verbosity = verbosity;

    this.get_application_id();

    // might want to get these from the environment in the future
    this.port = DEFAULT_PORT;
    this.redirect_uri = DEFAULT_REDIRECT_URI;
    this.landing_uri = process.env.REDIRECT_LANDING_URI || DEFAULT_LANDING_URI + this.app_id;

    this.oauth_token_dir = process.env.PINTEREST_OAUTH_TOKEN_DIR || DEFAULT_OAUTH_TOKEN_DIR;

    // swizzle oauth and api hosts, based on environment
    this.oauth_uri = process.env.PINTEREST_OAUTH_URI || DEFAULT_OAUTH_URI;
    this.api_uri = process.env.PINTEREST_API_URI || DEFAULT_API_URI;

    // start the global-agent to take care of any required proxies
    bootstrap();
  }

  /**
   * Get Pinterest application ID and secret from the OS environment.
   * It is best practice not to store credentials in code nor to provide
   * credentials on a shell command line.
   *
   * Exit with error code 1 (argument error) if the application id and secret
   * can not be found in the environment.
   */
  get_application_id() {
    const env_app_id = 'PINTEREST_APP_ID';
    const env_app_secret = 'PINTEREST_APP_SECRET';

    this.app_id = process.env[env_app_id];
    this.app_secret = process.env[env_app_secret];

    if (this.app_id && this.app_secret) {
      if (this.verbosity >= 2) {
        console.log(`Using application ID and secret from ${env_app_id} and ${env_app_secret}.`);
      }
      return;
    }

    throw new Error(`${env_app_id} and ${env_app_secret} must be set in the environment.`);
  }

  credentials_warning() {
    console.log('WARNING: This log has clear text credentials that need to be protected.');
  }
}
