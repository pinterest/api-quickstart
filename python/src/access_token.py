import base64
import hashlib
import requests

import user_auth

class AccessToken:
    def __init__(self, api_config, scopes=None, refreshable=True):
        print('getting auth_code...')
        auth_code = user_auth.get_auth_code(api_config, scopes=scopes, refreshable=refreshable)

        print('exchanging auth_code for access_token...')
        auth = api_config.app_id + ':' + api_config.app_secret
        b64auth = base64.b64encode(auth.encode('ascii')).decode('ascii')
        self.api_uri = api_config.api_uri
        # use the recommended authorization approach
        self.auth_headers = {'Authorization': 'Basic ' + b64auth}
        self._exchange_auth_code(auth_code, api_config.redirect_uri)

    def _exchange_auth_code(self, auth_code, redirect_uri):
        put_data = {'code': auth_code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'}
        response = requests.put(self.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        respdict = response.json()
        print('status: ' + respdict['status'])
        """
        The scope returned in the response includes all of the scopes that
        have been approved now or in the past by the user.
        """
        print('scope: ' + respdict['scope'])
        self.access_token = respdict['access_token']
        self.refresh_token = respdict['data'].get('refresh_token')
        if self.refresh_token:
            print('received refresh token')

    def header(self, headers={}):
        headers['Authorization'] = 'Bearer ' + self.access_token
        return headers

    def hashed(self):
        """
        Print the access code in a human-readable format that does not reveal
        the actual access credential. The purpose of this method is for a developer
        to verify that the access token has changed after a refresh.
        """
        return hashlib.sha256(self.access_token.encode()).hexdigest()

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError('AccessToken does not have a refresh token')
        print('refreshing access_token...')
        put_data = {'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token}
        response = requests.put(self.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        self.access_token = response.json()['access_token']
