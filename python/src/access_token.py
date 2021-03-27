import base64
import hashlib
import json
import pathlib
import requests

import user_auth

class AccessToken:
    def __init__(self, api_config, name='access_token'):
        self.api_config = api_config
        self.name = name
        self.path = pathlib.Path(api_config.oauth_token_dir) / (name + '.json')

        # use the recommended authorization approach
        auth = api_config.app_id + ':' + api_config.app_secret
        b64auth = base64.b64encode(auth.encode('ascii')).decode('ascii')
        self.auth_headers = {'Authorization': 'Basic ' + b64auth}

    def oauth(self, scopes=None, refreshable=True):
        print('getting auth_code...')
        auth_code = user_auth.get_auth_code(self.api_config, scopes=scopes, refreshable=refreshable)
        print(f'exchanging auth_code for {self.name}...')
        self._exchange_auth_code(auth_code)

    def _exchange_auth_code(self, auth_code):
        put_data = {'code': auth_code,
                    'redirect_uri': self.api_config.redirect_uri,
                    'grant_type': 'authorization_code'}
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',
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

    def read_or_oauth(self, scopes=None, refreshable=True):
        try:
            read()
        except:
            print(f'reading {self.name} failed')
            oauth(scopes=scopes, refreshable=refreshable)

    def read(self):
        with open(self.path, 'r') as jsonfile:
            data = json.load(jsonfile)
            self.name = data['name']
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']

    def write(self):
        with open(self.path, 'w') as jsonfile:
            json.dump({'name': self.name,
                       'access_token': self.access_token,
                       'refresh_token': self.refresh_token},
                      jsonfile,
                      indent=2)

    def header(self, headers={}):
        headers['Authorization'] = 'Bearer ' + self.access_token
        return headers

    def hashed(self):
        """
        Print the access token in a human-readable format that does not reveal
        the actual access credential. The purpose of this method is for a developer
        to verify that the access token has changed after a refresh.
        """
        return hashlib.sha256(self.access_token.encode()).hexdigest()

    def hashed_refresh_token(self):
        """
        Print the refresh token in a human-readable format that does not reveal
        the actual access credential. The purpose of this method is for a developer
        to verify when the refresh token changes.
        """
        if not self.refresh_token:
            raise RuntimeError('AccessToken does not have a refresh token')
        return hashlib.sha256(self.refresh_token.encode()).hexdigest()

    def refresh(self):
        if not self.refresh_token:
            raise RuntimeError('AccessToken does not have a refresh token')
        print(f'refreshing {self.name}...')
        put_data = {'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token}
        response = requests.put(self.api_config.api_uri + '/v3/oauth/access_token/',
                                headers=self.auth_headers, data=put_data)
        print(response)
        self.access_token = response.json()['access_token']
