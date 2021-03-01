import base64
import json
import requests

import user_auth

class AccessToken:
    def __init__(self, api_config, refreshable=True):
        print('getting auth_code...')
        auth_code = user_auth.get_auth_code(api_config, refreshable)

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
        respdict = json.loads(response.text)
        print('status: ' + respdict['status'])
        print('scope: ' + respdict['scope'])
        self.access_token = respdict['access_token']
        self.refresh_token = respdict['data'].get('refresh_token')
        if self.refresh_token:
            print('received refresh token')

    def header(self, headers={}):
        headers['Authorization'] = 'Bearer ' + self.access_token
        return headers

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError('AccessToken does not have a refresh token')
        print('refreshing access_token...')
        put_data = {'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token}
        response = requests.put(self.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        respdict = json.loads(response.text)
        self.access_token = respdict['access_token']
