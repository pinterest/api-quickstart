import got from 'got';

import { AccessTokenCommon } from '../access_token_common.js';
import { Scope } from './oauth_scope.js';
import get_auth_code from '../user_auth.js';

export class AccessToken extends AccessTokenCommon {
  constructor(api_config, { name }) {
    super(api_config, { name: name });
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

  async refresh() {
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
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }
}
