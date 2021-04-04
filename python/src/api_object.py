import requests

class ApiObject:
    def __init__(self, api_config, access_token):
        self.api_uri = api_config.api_uri
        self.api_config = api_config
        self.access_token = access_token

    def _unpack(self, response):
        if self.api_config.verbosity >= 1:
            print(response)
        if self.api_config.verbosity >= 3:
            print(response.json())
        if response.ok:
            return response.json()['data']
        else:
            print('request failed with reason: ' + response.reason)
            return {}

    def request_data(self, path):
        if self.api_config.verbosity >= 2:
            print(f'GET {self.api_uri + path}')
        response = requests.get(self.api_uri + path, headers=self.access_token.header())
        return self._unpack(response)

    def post_data(self, path):
        if self.api_config.verbosity >= 2:
            print(f'POST {self.api_uri + path}')
        response = requests.post(self.api_uri + path, headers=self.access_token.header())
        return self._unpack(response)
