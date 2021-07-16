import requests

from access_token_common import AccessTokenCommon
from user_auth import get_auth_code

class AccessToken(AccessTokenCommon):
    def __init__(self, api_config, name=None):
        super().__init__(api_config, name)

    def oauth(self, scopes=None, refreshable=True):
        """
        Execute the OAuth 2.0 process for obtaining an access token.
        For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
        and https://developers.pinterest.com/docs/redoc/#tag/Authentication
        """
        print('getting auth_code...')
        auth_code = get_auth_code(self.api_config, scopes=scopes, refreshable=refreshable)
        print(f'exchanging auth_code for {self.name}...')
        self.exchange_auth_code(auth_code)

    def exchange_auth_code(self, auth_code):
        """
        Call the Pinterest API to exchange the auth_code (obtained by
        a redirect from the browser) for the access_token and (if requested)
        refresh_token.
        """
        put_data = {'code': auth_code,
                    'redirect_uri': self.api_config.redirect_uri,
                    'grant_type': 'authorization_code'}
        if (self.api_config.verbosity >= 2):
            print('PUT', self.api_config.api_uri + '/v3/oauth/access_token/')
            if (self.api_config.verbosity >= 3):
                self.api_config.credentials_warning();
                print(put_data)
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        unpacked = self.unpack(response)
        print('status: ' + unpacked['status'])

        """
        The scope returned in the response includes all of the scopes that
        have been approved now or in the past by the user.
        """
        print('scope: ' + unpacked['scope'])
        self.access_token = unpacked['access_token']
        self.refresh_token = unpacked['data'].get('refresh_token')
        self.scopes = unpacked['scope']
        if self.refresh_token:
            print('received refresh token')

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError('AccessToken does not have a refresh token')
        print(f'refreshing {self.name}...')
        put_data = {'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token}
        if (self.api_config.verbosity >= 2):
            print('PUT', self.api_config.api_uri + '/v3/oauth/access_token/')
            if (self.api_config.verbosity >= 3):
                self.api_config.credentials_warning();
                print(put_data)
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',

                                headers=self.auth_headers, data=put_data)
        unpacked = self.unpack(response)
        self.access_token = unpacked['access_token']
