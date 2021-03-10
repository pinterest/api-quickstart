import mock

from integration_mocks import IntegrationMocks

class GetAccessTokenTest(IntegrationMocks):
    def mock_requests_put(self, uri, headers=None, data=None):
        print('mock_requests_put', uri, headers, data)
        self.put_uri = uri
        self.requests_put_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'status': 'test-status',
                                      'scope': 'test-scope',
                                      'access_token': 'test-access-token',
                                      'data': {'refresh_token': 'test-refresh-token'}
                                      }
        return response

    def mock_requests_get(self, uri, headers=None, data=None):
        print('mock_requests_get', uri, headers, data)
        self.get_uri = uri
        self.requests_get_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'data':
                                      {'full_name': 'test fullname',
                                       'about': 'test about',
                                       'profile_url': 'test profile url',
                                       'pin_count': 'pin count'
                                       }
                                      }
        return response

    def test_get_access_token(self):
        from scripts.get_access_token import main # import here to see monkeypatches

        self.requests_put_calls = 0
        self.requests_get_calls = 0

        with self.mock_redirect():
            main() # run get_access_token

        # put called once for access_token
        self.assertEqual(self.requests_put_calls, 1)
        self.assertEqual(self.put_uri, 'https://api.pinterest.com/v3/oauth/access_token/')

        # get called once for user data
        self.assertEqual(self.requests_get_calls, 1)
        self.assertEqual(self.get_uri, 'https://api.pinterest.com/v3/users/me/')
