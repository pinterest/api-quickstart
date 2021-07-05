import requests

from access_token_common import AccessTokenCommon

class AccessToken(AccessTokenCommon):
    def __init__(self, api_config, name=None):
        super().__init__(api_config, name)

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
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        respdict = response.json()
        print('status: ' + respdict['status'])
        if (self.api_config.verbosity >= 3):
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
        """
        The scope returned in the response includes all of the scopes that
        have been approved now or in the past by the user.
        """
        print('scope: ' + respdict['scope'])
        self.access_token = respdict['access_token']
        self.refresh_token = respdict['data'].get('refresh_token')
        self.scopes = respdict['scope']
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
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        if (self.api_config.verbosity >= 3):
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
        self.access_token = response.json()['access_token']
