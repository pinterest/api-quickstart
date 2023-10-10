import crypto from 'crypto';
import fs from 'fs';
import got from 'got';
import path from 'path';

import { ApiCommon } from './api_common.js';
import { Scope } from './oauth_scope.js';
import get_auth_code from './user_auth.js';

export class AccessToken extends ApiCommon {
  constructor(api_config, { name }) {
    super(api_config);

    const auth = `${api_config.app_id}:${api_config.app_secret}`;
    const b64auth = Buffer.from(auth).toString('base64');
    this.api_uri = api_config.api_uri;
    this.auth_headers = { Authorization: `Basic ${b64auth}` };
    this.name = name || 'access_token';
    this.path = path.join(api_config.oauth_token_dir, `${this.name}.json`);
  }

  /**
   * This method tries to make it as easy as possible for a developer
   * to start using an OAuth access token. It fetches the access token
   * by trying all supported methods, in this order:
   *    1. Get from the process environment variable that is the UPPER CASE
   *       version of the this.name attribute. This method is intended as
   *       a quick hack for developers.
   *    2. Read the access_token and (if available) the refresh_token from
   *       the file at the path specified by joining the configured
   *       OAuth token directory, the this.name attribute, and the '.json'
   *       file extension.
   *    3. Execute the OAuth 2.0 request flow using the default browser
   *       and local redirect.
   */
  async fetch({ scopes = null, refreshable = true }) {
    try {
      this.from_environment();
      return;
    } catch (err) {
      console.log(`reading ${this.name} from environment failed, trying read`);
      if (this.api_config.verbosity >= 3) {
        console.log('  because...', err);
      }
    }

    try {
      this.read();
      return;
    } catch (err) {
      console.log(`reading ${this.name} failed, trying oauth`);
      if (this.api_config.verbosity >= 3) {
        console.log('  because...', err);
      }
    }

    await this.oauth({ scopes: scopes, refreshable: refreshable });
  }

  /**
   * Easiest path for using an access token: get it from the
   * process environment. Note that the environment variable name
   * is the UPPER CASE of the this.name instance attribute.
   */
  from_environment() {
    const env_access_token = process.env[this.name.toUpperCase()];
    if (env_access_token) {
      this.access_token = env_access_token;
      this.refresh_token = null;
    } else {
      throw new Error('No access token in the environment');
    }
  }

  /* Get the access token from the file at this.path. */
  read() {
    const data = JSON.parse(fs.readFileSync(this.path));
    this.name = data.name || 'access_token';
    const access_token = data.access_token;
    if (!access_token) {
      throw new Error('Access token not found in JSON file');
    }
    this.access_token = access_token;
    this.refresh_token = data.refresh_token;
    this.scopes = data.scopes;
    console.log(`read ${this.name} from ${this.path}`);
  }

  /* Store the access token in the file at this.path. */
  write() {
    const json = JSON.stringify({
      name: this.name,
      access_token: this.access_token,
      refresh_token: this.refresh_token,
      scopes: this.scopes
    }, null, 2);
    /* Make credentials-bearing file as secure as possible with mode 0o600. */
    fs.open(this.path, 'w', 0o600, (err, fd) => {
      if (err) {
        throw new Error(`Can not open file for write: ${this.path}`);
      }
      fs.write(fd, json, (err, written, string) => {
        if (err) {
          throw new Error(`Can not write file: ${this.path}`);
        }
      });
    });
  }

  header(headers = {}) {
    headers.Authorization = `Bearer ${this.access_token}`;
    return headers;
  }

  hashed() {
    return crypto.createHash('sha256').update(this.access_token).digest('hex');
  }

  /**
   * Print the refresh token in a human-readable format that does not reveal
   * the actual access credential. The purpose of this method is for a developer
   * to verify when the refresh token changes.
   */
  hashed_refresh_token() {
    if (!this.refresh_token) {
      throw new Error('AccessToken does not have a refresh token');
    }
    return crypto.createHash('sha256').update(this.refresh_token).digest('hex');
  }

  /**
   * Execute the OAuth 2.0 process for obtaining an access token.
   * For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
   * and https://developers.pinterest.com/docs/api/v5/#tag/oauth
   *
   * For v5, scopes are required and tokens must be refreshable.
   *
   * Constructor may not be async, so OAuth must be performed as a separate method.
   */
  async oauth({ scopes = null, refreshable = true }) {
    if (!scopes) {
      scopes = [Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS];
      console.log('v5 requires scopes for OAuth. setting to default: READ_USERS,READ_PINS,READ_BOARDS');
    }

    if (!refreshable) {
      throw new Error('Pinterest API v5 only provides refreshable OAuth access tokens');
    }

    console.log('getting auth_code...');
    const auth_code = await get_auth_code(this.api_config,
      { scopes: scopes, refreshable: refreshable });

    console.log('exchanging auth_code for access_token...');
    try {
      const post_data = {
        code: auth_code,
        redirect_uri: this.api_config.redirect_uri,
        grant_type: 'authorization_code'
      };
      if (this.api_config.verbosity >= 2) {
        console.log('POST', `${this.api_uri}/v5/oauth/token`);
        if (this.api_config.verbosity >= 3) {
          this.api_config.credentials_warning();
          console.log(post_data);
        }
      }
      const response = await got.post(`${this.api_uri}/v5/oauth/token`, {
        headers: this.auth_headers, // use the recommended authorization approach
        form: post_data, // send body as x-www-form-urlencoded
        responseType: 'json'
      });
      this.print_response(response);

      // The scope returned in the response includes all of the scopes that
      // have been approved now or in the past by the user.
      console.log('scope:', response.body.scope);
      this.scopes = response.body.scope;
      this.access_token = response.body.access_token;
      this.refresh_token = response.body.refresh_token;
      if (this.refresh_token) {
        console.log('received refresh token');
      }
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }

  async refresh({ everlasting = false }) {
    // There should be a refresh_token, but it is best to check.
    if (!this.refresh_token) {
      throw new Error('AccessToken does not have a refresh token');
    }

    console.log('refreshing access_token...');
    let response;
    try {
      const post_data = {
        grant_type: 'refresh_token',
        refresh_token: this.refresh_token
      };
      if (everlasting) {
        post_data.refresh_on = true;
      }
      if (this.api_config.verbosity >= 2) {
        console.log('POST', `${this.api_uri}/v5/oauth/token`);
        if (this.api_config.verbosity >= 3) {
          this.api_config.credentials_warning();
          console.log(post_data);
        }
      }
      response = await got.post(`${this.api_uri}/v5/oauth/token`, {
        headers: this.auth_headers,
        form: post_data, // send body as x-www-form-urlencoded
        responseType: 'json'
      });
      this.print_response(response);
      this.access_token = response.body.access_token;
      if (response.body.refresh_token) {
        console.log('received refresh token');
        this.refresh_token = response.body.refresh_token;
      }
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }
}
