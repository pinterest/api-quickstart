import got from 'got'

import {AccessTokenCommon} from '../access_token_common.js'
import get_auth_code from '../user_auth.js'

export class AccessToken extends AccessTokenCommon {

  constructor(api_config, {name = null}) {
    super(api_config, {name: name});
  }

  // constructor may not be async, so OAuth must be performed as a separate method.
  async oauth({scopes=null, refreshable=true}) {
    console.log('getting auth_code...');
    const auth_code = await get_auth_code(this.api_config,
                                          {scopes:scopes, refreshable:refreshable});

    console.log('exchanging auth_code for access_token...');
    var response;
    try {
      if (this.api_config.verbosity >= 2) {
        console.log('PUT', this.api_uri + '/v3/oauth/access_token/');
      }
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
    if (this.api_config.verbosity >= 3) {
      console.log('x-pinterest-rid:', response.headers['x-pinterest-rid']);
    }
    // The scope returned in the response includes all of the scopes that
    // have been approved now or in the past by the user.
    console.log('scope: ' + response.body.scope);
    this.access_token = response.body.access_token;
    this.refresh_token = response.body.data.refresh_token;
    if (this.refresh_token) {
      console.log('received refresh token');
    }
  }

  async refresh() {
    // There should be a refresh_token, but it is best to check.
    if (!this.refresh_token) {
      throw 'AccessToken does not have a refresh token';
    }

    console.log('refreshing access_token...');
    var response;
    try {
      if (this.api_config.verbosity >= 2) {
        console.log('PUT', this.api_uri + '/v3/oauth/access_token/');
      }
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
