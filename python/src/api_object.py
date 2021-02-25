import json
import requests

class ApiObject:
    def __init__(self, api_config, access_token):
        self.api_uri = api_config.api_uri
        self.access_token = access_token

    def request_data(self, path):
        response = requests.get(self.api_uri + path, headers=self.access_token.header())
        print(response)
        if response.ok:
            return json.loads(response.text)['data']
        else:
            print('request failed with reason: ' + response.reason)
            return {}
