import unittest
import mock

from src.access_token import AccessToken

class AccessTokenTest(unittest.TestCase):

    @mock.patch('src.access_token.requests.put')
    @mock.patch('src.access_token.user_auth.get_auth_code')
    def test_access_token(self, mock_get_auth_code, mock_requests_put):
        mock_get_auth_code.return_value = 'test-auth-code'

        mock_api_config = mock.Mock()
        mock_api_config.app_id = 'test-app-id'
        mock_api_config.app_secret = 'test-app-secret'
        mock_api_config.api_uri = 'test-api-uri'
        mock_api_config.redirect_uri = 'test-redirect-uri'

        mock_response = mock.MagicMock()
        mock_response.__str__.return_value = '<Response [200]>'
        mock_response.json.return_value = {'status': 'test-stats',
                                           'scope': 'test-scope',
                                           'access_token': 'test-access-token',
                                           'data': {'refresh_token': 'test-refresh-token'}
                                           }
        mock_requests_put.return_value = mock_response
        
        access_token = AccessToken(mock_api_config)
        mock_get_auth_code.assert_called_once_with(mock_api_config,
                                                   scopes=None,
                                                   refreshable=True)
        mock_requests_put.assert_called_once_with(
            'test-api-uri/v3/oauth/access_token/',
            headers={'Authorization': 'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'},
            data={'code': 'test-auth-code',
                  'redirect_uri': 'test-redirect-uri',
                  'grant_type': 'authorization_code'})

        # header() should create a new headers dict if required
        test_header = {'Authorization': 'Bearer test-access-token'}
        header = access_token.header()
        self.assertEqual(header, test_header)

        # header() should merge with an existing headers dict and return it
        headers = {'this key': 'this value'}
        expected = headers.copy()
        expected.update(test_header)
        returned = access_token.header(headers=headers)
        self.assertEqual(headers, expected)
        self.assertEqual(headers, returned)

        # verify that the SHA256 hash works
        # echo -n test-access-token | shasum -a 256
        self.assertEqual(access_token.hashed(),
                         '597480d4b62ca612193f19e73fe4cc3ad17f0bf9cfc16a7cbf4b5064131c4805')

        mock_response = mock.MagicMock()
        mock_response.__str__.return_value = '<Response [200]>'
        mock_response.json.return_value = {'access_token': 'new-access-token'}
        mock_requests_put.reset_mock()
        mock_requests_put.return_value = mock_response

        # verify that refresh works by using the sha256 of 'new-access-token'
        access_token.refresh()
        # echo -n new-access-token | shasum -a 256
        self.assertEqual(access_token.hashed(),
                         '25b416c373e247768cc1a3ed4a20a13888f6b9f5288378f4756ce227d05b7710')
        mock_requests_put.assert_called_once_with(
            'test-api-uri/v3/oauth/access_token/',
            headers={'Authorization': 'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'},
            data={'grant_type': 'refresh_token',
                  'refresh_token': 'test-refresh-token'})

        # verify behavior with non-default arguments:
        # - scopes passed to get_auth_code
        # - refresh raises an exception
        mock_response.json.return_value = {'status': 'test-stats',
                                           'scope': 'test-scope-1,test-scope-2',
                                           'access_token': 'test-access-token',
                                           'data': {}
                                           }
        mock_get_auth_code.reset_mock()
        access_token = AccessToken(mock_api_config,
                                   scopes=['test-scope-1','test-scope-2'],
                                   refreshable=False)
        mock_get_auth_code.assert_called_once_with(mock_api_config,
                                                   scopes=['test-scope-1','test-scope-2'],
                                                   refreshable=False)
        with self.assertRaisesRegex(RuntimeError, 'AccessToken does not have a refresh token'):
            access_token.refresh()
