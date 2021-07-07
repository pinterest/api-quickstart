import got from 'got'

import {AccessTokenCommon} from '../access_token_common.js'
import {Scope} from './oauth_scope.js'
import get_auth_code from '../user_auth.js'

export class AccessToken extends AccessTokenCommon {

  constructor(api_config, {name = null}) {
    super(api_config, {name: name});
  }

  /**
   * Execute the OAuth 2.0 process for obtaining an access token.
   * For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
   *
   * For v5, scopes are required and tokens must be refreshable.
   *
   * Constructor may not be async, so OAuth must be performed as a separate method.
   */
  async oauth({scopes=null, refreshable=true}) {
    if (!scopes) {
      scopes = [Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS];
      console.log('v5 requires scopes for OAuth. setting to default: READ_USERS,READ_PINS,READ_BOARDS');
    }

    if (!refreshable) {
      throw 'Pinterest API v5 only provides refreshable OAuth access tokens';
    }

    console.log('getting auth_code...');
    const auth_code = await get_auth_code(this.api_config,
                                          {scopes:scopes, refreshable:refreshable});

    console.log('exchanging auth_code for access_token...');
    var response;
    try {
      if (this.api_config.verbosity >= 2) {
        console.log('POST', this.api_uri + '/v5/oauth/token');
      }
      response = await got.post(this.api_uri + '/v5/oauth/token', {
        headers: this.auth_headers, // use the recommended authorization approach
        form: { // send body as x-www-form-urlencoded
          'code': auth_code,
          'redirect_uri': this.api_config.redirect_uri,
          'grant_type': 'authorization_code'
        },
        responseType: 'json'
      })
    } catch (error) {
      // console.log('error:', error);
      console.log(`<Response [${error.response.statusCode}]>`);
      console.log('request failed with reason:', error.response.body.message);
      throw 'OAuth failed because... ' + error.response.body.message;
    }

    console.log(`<Response [${response.statusCode}]>`);
    if (this.api_config.verbosity >= 3) {
      console.log('x-pinterest-rid:', response.headers['x-pinterest-rid']);
    }
    // The scope returned in the response includes all of the scopes that
    // have been approved now or in the past by the user.
    console.log('scope: ' + response.body.scope);
    this.scopes = response.body.scope;
    this.access_token = response.body.access_token;
    this.refresh_token = response.body.refresh_token;
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
        console.log('POST', this.api_uri + '/v5/oauth/token');
      }
      response = await got.post(this.api_uri + '/v5/oauth/token', {
        headers: this.auth_headers,
        form: { // send body as x-www-form-urlencoded
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
