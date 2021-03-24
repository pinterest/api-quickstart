import crypto from 'crypto'
import got from 'got'

import get_auth_code from './user_auth.js'

export default class AccessToken {

  constructor(api_config, {scopes = null, refreshable = true}) {
    const auth = api_config.app_id + ':' + api_config.app_secret;
    const b64auth = Buffer.from(auth).toString('base64');
    this.api_config = api_config;
    this.api_uri = api_config.api_uri;
    this.auth_headers = {'Authorization': 'Basic ' + b64auth}
    this.scopes = scopes;
    this.refreshable = refreshable;
  }

  // constructor may not be async, so OAuth must be performed as a separate method.
  async oauth() {
    console.log('getting auth_code...');
    const auth_code = await get_auth_code(this.api_config,
                                          {scopes: this.scopes,
                                           refreshable: this.refreshable});

    console.log('exchanging auth_code for access_token...');
    var response;
    try {
      response = await got.put(this.api_uri + '/v3/oauth/access_token/', {
        headers: this.auth_headers, // use the recommended authorization approach
        json: {
          'code': auth_code,
          'redirect_uri': this.api_config.redirect_uri,
          'grant_type': 'authorization_code'
        },
        responseType: 'json'
      })
    } catch (error) {
      console.log(`<Response [${error.response.statusCode}]>`);
      console.log('request failed with reason:', error.response.body.message);
      throw 'OAuth failed because... ' + error.response.body.message;
    }

    console.log(`<Response [${response.statusCode}]>`);
    console.log('status: ' + response.body.status);
    // The scope returned in the response includes all of the scopes that
    // have been approved now or in the past by the user.
    console.log('scope: ' + response.body.scope);
    this.access_token = response.body.access_token;
    this.refresh_token = response.body.data.refresh_token;
    if (this.refresh_token) {
      console.log('received refresh token');
    }
  }

  header(headers = {}) {
    headers['Authorization'] = 'Bearer ' + this.access_token;
    return headers;
  }

  hashed() {
    return crypto.createHash('sha256').update(this.access_token).digest('hex')
  }

  async refresh() {
    // AccessToken must be initialized as refreshable.
    if (!this.refreshable) {
      throw 'Access Token is not refreshable.';
    }

    // There should be a refresh_token, but it is best to check.
    if (!this.refresh_token) {
      throw 'Refresh Token is not available.';
    }

    console.log('refreshing access_token...');
    var response;
    try {
      response = await got.put(this.api_uri + '/v3/oauth/access_token/', {
        headers: this.auth_headers,
        json: {
          'grant_type': 'refresh_token',
          'refresh_token': this.refresh_token
        },
        responseType: 'json'
      })
    } catch (error) {
      console.log(`<Response [${error.response.statusCode}]>`);
      console.log('request failed with reason:', error.response.body.message);
      throw 'AccessToken refresh failed because... ' + error.response.body.message;
    }
    console.log(`<Response [${response.statusCode}]>`);
    this.access_token = response.body.access_token;
  }
}
