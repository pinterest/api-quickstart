import crypto from 'crypto'
import fs from 'fs';
import path from 'path'

import {ApiCommon} from './api_common.js'

export class AccessTokenCommon extends ApiCommon {

  constructor(api_config, {name = null}) {
    super();

    const auth = api_config.app_id + ':' + api_config.app_secret;
    const b64auth = Buffer.from(auth).toString('base64');
    this.api_config = api_config;
    this.api_uri = api_config.api_uri;
    this.auth_headers = {'Authorization': 'Basic ' + b64auth}
    if (name) {
      this.name = name;
    } else {
      this.name = 'access_token_' + api_config.version;
    }
    this.path = path.join(api_config.oauth_token_dir, this.name + '.json')
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
  async fetch({scopes=null, refreshable=true}) {
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

    await this.oauth({scopes:scopes, refreshable:refreshable});
  }

  // constructor may not be async, so OAuth must be performed as a separate method.
  async oauth({scopes=null, refreshable=true}) {
    console.log('refresh() must be overriden.')
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
      throw 'No access token in the environment';
    }
  }

  /* Get the access token from the file at this.path. */
  read() {
    const data = JSON.parse(fs.readFileSync(this.path));
    this.name = data.name || 'access_token';
    const access_token = data.access_token;
    if (!access_token) {
      throw 'Access token not found in JSON file';
    }
    this.access_token = access_token;
    this.refresh_token = data.refresh_token;
    this.scopes = data.scopes;
    console.log(`read ${this.name} from ${this.path}`);
  }

  /* Store the access token in the file at this.path. */
  write() {
    const output = {'name': this.name,
                    'access_token': this.access_token,
                    'refresh_token': this.refresh_token,
                    'scopes': this.scopes
                   }
    const json = JSON.stringify(output, null, 2)
    /* Make credentials-bearing file as secure as possible with mode 0o600. */
    fs.open(this.path, 'w', 0o600, (err, fd) => {
      if (err) {
        throw 'Can not open file for write: ' + this.path;
      }
      fs.write(fd, json, (err, written, string) => {
        if (err) {
          throw 'Can not write file: ' + this.path;
        }
      })
    })
  }

  header(headers = {}) {
    headers['Authorization'] = 'Bearer ' + this.access_token;
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
      throw 'AccessToken does not have a refresh token';
    }
    return crypto.createHash('sha256').update(this.refresh_token).digest('hex');
  }

  async refresh() {
    console.log('refresh() must be overriden.')
  }
}
