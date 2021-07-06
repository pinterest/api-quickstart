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

        For v5, scopes are required and tokens must be refreshable.
        """
        if not scopes:
            raise ValueError('Pinterest API v5 requires scopes for OAuth')

        if not refreshable:
            raise ValueError('Pinterest API v5 only provides refreshable OAuth access tokens')

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
        post_data = {'code': auth_code,
                     'redirect_uri': self.api_config.redirect_uri,
                     'grant_type': 'authorization_code'}
        if (self.api_config.verbosity >= 2):
            print('POST', self.api_config.api_uri + '/v5/oauth/token')
        response = requests.post(self.api_config.api_uri + '/v5/oauth/token',
                                 headers=self.auth_headers, data=post_data)
        print(response)
        respdict = response.json()
        if (self.api_config.verbosity >= 3):
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))

        print('scope: ' + respdict['scope'])
        self.access_token = respdict['access_token']
        self.refresh_token = respdict['refresh_token']
        self.scopes = respdict['scope']

    def refresh(self):
        print(f'refreshing {self.name}...')
        post_data = {'grant_type': 'refresh_token',
                     'refresh_token': self.refresh_token}
        if (self.api_config.verbosity >= 2):
            print('POST', self.api_config.api_uri + '/v5/oauth/token')
        response = requests.post(self.api_config.api_uri + '/v5/oauth/token',
                                 headers=self.auth_headers, data=post_data)
        print(response)
        if (self.api_config.verbosity >= 3):
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
        self.access_token = response.json()['access_token']
