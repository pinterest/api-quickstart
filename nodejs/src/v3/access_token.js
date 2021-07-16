import got from 'got'

import {AccessTokenCommon} from '../access_token_common.js'
import get_auth_code from '../user_auth.js'

export class AccessToken extends AccessTokenCommon {

  constructor(api_config, {name}) {
    super(api_config, {name: name});
  }

  /**
   * Execute the OAuth 2.0 process for obtaining an access token.
   * For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
   * and https://developers.pinterest.com/docs/redoc/#tag/Authentication
   *
   * Constructor may not be async, so OAuth must be performed as a separate method.
   */
  async oauth({scopes=null, refreshable=true}) {
    console.log('getting auth_code...');
    const auth_code = await get_auth_code(this.api_config,
                                          {scopes:scopes, refreshable:refreshable});

    console.log('exchanging auth_code for access_token...');
    try {
      const put_data = {
        code: auth_code,
        redirect_uri: this.api_config.redirect_uri,
        grant_type: 'authorization_code'
      };
      if (this.api_config.verbosity >= 2) {
        console.log('PUT', `${this.api_uri}/v3/oauth/access_token/`);
        if (this.api_config.verbosity >= 3) {
          this.api_config.credentials_warning();
          console.log(put_data);
        }
      }
      const response = await got.put(`${this.api_uri}/v3/oauth/access_token/`, {
        headers: this.auth_headers, // use the recommended authorization approach
        json: put_data,
        responseType: 'json'
      })
      this.print_response(response);
      console.log('status:', response.body.status);

      // The scope returned in the response includes all of the scopes that
      // have been approved now or in the past by the user.
      console.log('scope:', response.body.scope);
      this.scopes = response.body.scope;
      this.access_token = response.body.access_token;
      this.refresh_token = response.body.data.refresh_token;
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
      throw 'AccessToken does not have a refresh token';
    }

    console.log('refreshing access_token...');
    try {
      const put_data = {
        grant_type: 'refresh_token',
        refresh_token: this.refresh_token
      };
      if (this.api_config.verbosity >= 2) {
        console.log('PUT', `${this.api_uri}/v3/oauth/access_token/`);
        if (this.api_config.verbosity >= 3) {
          this.api_config.credentials_warning();
          console.log(put_data);
        }
      }
      const response = await got.put(`${this.api_uri}/v3/oauth/access_token/`, {
        headers: this.auth_headers,
        json: put_data,
        responseType: 'json'
      })
      this.print_response(response)
      this.access_token = response.body.access_token;
    } catch (error) {
      this.print_and_throw_error(error);
    }
  }
}
