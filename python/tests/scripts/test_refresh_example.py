import mock

from integration_mocks import IntegrationMocks

class RefreshExampleTest(IntegrationMocks):
    def mock_requests_put(self, uri, headers=None, data=None):
        print('mock_requests_put', uri, headers, data)
        self.requests_put_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'status': 'test-status',
                                      'scope': 'test-scope',
                                      # response needs to be different each time
                                      'access_token': 'test-access-token-' + str(self.requests_put_calls),
                                      'data': {'refresh_token': 'test-refresh-token'}
                                      }
        return response

    def mock_requests_get(self, uri, headers=None, data=None):
        print('mock_requests_get', uri, headers, data)
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
        from scripts.refresh_example import main # import here to see monkeypatches

        self.requests_put_calls = 0

        with self.mock_redirect():
            main() # run refresh_example

        self.assertEqual(self.requests_put_calls, 3)
