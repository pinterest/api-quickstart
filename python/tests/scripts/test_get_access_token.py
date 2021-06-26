import mock
import sys

from integration_mocks import IntegrationMocks

class GetAccessTokenTest(IntegrationMocks):
    def mock_requests_put(self, uri, headers=None, data=None, allow_redirects=True):
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

    def mock_requests_get(self, uri, headers=None, data=None, allow_redirects=True):
        print('mock_requests_get', uri, headers, data)
        self.get_uri = uri
        self.requests_get_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'data':
                                      {'full_name': 'test fullname',
                                       'id': 'test user id',
                                       'about': 'test about',
                                       'profile_url': 'test profile url',
                                       'pin_count': 'pin count'
                                       }
                                      }
        return response

    @mock.patch('builtins.print')
    def test_get_access_token(self, mock_print):
        from scripts.get_access_token import main # import here to see monkeypatches

        self.requests_put_calls = 0
        self.requests_get_calls = 0

        with mock.patch('builtins.open') as mock_open:
            with mock.patch.dict('os.environ', self.mock_os_environ, clear=True):
                mock_open.side_effect = FileNotFoundError # no access_token.json file
                with self.mock_redirect():
                    main() # run get_access_token

        # put called once for access_token
        self.assertEqual(self.requests_put_calls, 1)
        self.assertEqual(self.put_uri, 'https://api.pinterest.com/v3/oauth/access_token/')

        # get called once for user data
        self.assertEqual(self.requests_get_calls, 1)
        self.assertEqual(self.get_uri, 'https://api.pinterest.com/v3/users/me/')

        # verify expected values printed. see unit tests for values
        mock_print.assert_any_call('mock_open_new: ' +
                                   'https://www.pinterest.com/oauth/?consumer_id=test-app-id' +
                                   '&redirect_uri=http://localhost:8085/&response_type=code&' +
                                   'refreshable=True')
        mock_print.assert_any_call('hashed access token: ' +
                                   '597480d4b62ca612193f19e73fe4cc3ad17f0bf9cfc16a7cbf4b5064131c4805')
        mock_print.assert_any_call('hashed refresh token: ' +
                                   '0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde')
