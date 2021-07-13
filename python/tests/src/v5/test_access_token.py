import unittest
import mock
import json

from src.v5.access_token import AccessToken
from src.v5.oauth_scope import Scope

class AccessTokenTest(unittest.TestCase):

    @mock.patch('src.v5.access_token.requests.post')
    @mock.patch('src.v5.access_token.get_auth_code')
    def test_access_token(self, mock_get_auth_code, mock_requests_post):
        mock_get_auth_code.return_value = 'test-auth-code'

        mock_api_config = mock.Mock()
        mock_api_config.app_id = 'test-app-id'
        mock_api_config.app_secret = 'test-app-secret'
        mock_api_config.api_uri = 'test-api-uri'
        mock_api_config.redirect_uri = 'test-redirect-uri'
        mock_api_config.oauth_token_dir = 'test-token-dir'
        mock_api_config.version = 'v5'
        mock_api_config.verbosity = 2

        mock_response = mock.MagicMock()
        mock_response.__str__.return_value = '<Response [200]>'
        mock_response.json.return_value = {'status': 'test-status',
                                           'scope': 'test-scope',
                                           'access_token': 'test-access-token',
                                           'refresh_token': 'test-refresh-token'
                                           }
        mock_requests_post.return_value = mock_response

        access_token = AccessToken(mock_api_config)
        access_token.oauth()

        # mock does not figure out enum equality, so need to unpack arguments
        # of get_auth_code in order to check the default value for scopes.
        self.assertTrue(mock_get_auth_code.mock_calls[0][2]['refreshable'])
        scopes = mock_get_auth_code.mock_calls[0][2]['scopes']
        # convert from Scope enum to values
        values = list(map(lambda scope: scope.value, scopes))
        # verify the scopes used by the API
        self.assertEqual(['user_accounts:read','pins:read','boards:read'], values)

        # mock_get_auth_code.mock_calls[0][2]['scopes'])
        mock_requests_post.assert_called_once_with(
            'test-api-uri/v5/oauth/token',
            headers={'Authorization': 'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'},
            data={'code': 'test-auth-code',
                  'redirect_uri': 'test-redirect-uri',
                  'grant_type': 'authorization_code'})

        mock_response = mock.MagicMock()
        mock_response.__str__.return_value = '<Response [200]>'
        mock_response.json.return_value = {
            'access_token': 'pina_new-access-token',
            'refresh_token': 'pinr_new-refresh-token',
            'scope': 'users:read,pins:read,boards:read'
        }
        mock_response.headers = {'x-pinterest-rid': 'mock-request-id'}
        mock_requests_post.reset_mock()
        mock_requests_post.return_value = mock_response

        # verify that refresh works by using the sha256 of 'new-access-token'
        access_token.refresh()
        # echo -n pina_new-access-token | shasum -a 256
        self.assertEqual(access_token.hashed(),
                         '4e9a163e7e33428d50c6eda1305fa8f316aa9779578944ca5db4748acd22e8d2')
        mock_requests_post.assert_called_once_with(
            'test-api-uri/v5/oauth/token',
            headers={'Authorization': 'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'},
            data={'grant_type': 'refresh_token',
                  'refresh_token': 'test-refresh-token'})

        # verify behavior with non-default arguments:
        # - scopes passed to get_auth_code
        # - refresh raises an exception
        mock_response.json.return_value = {'status': 'test-stats',
                                           'scope': 'users:read,pins:read,boards:read',
                                           'access_token': 'test-access-token',
                                           'refresh_token': 'pinr_test-refresh-token',
                                           }
        mock_get_auth_code.reset_mock()
        access_token = AccessToken(mock_api_config)
        access_token.oauth(scopes=['test-scope-1','test-scope-2'],
                           refreshable=True)
        mock_get_auth_code.assert_called_once_with(mock_api_config,
                                                   scopes=['test-scope-1','test-scope-2'],
                                                   refreshable=True)

        with self.assertRaisesRegex(ValueError,
                                    'Pinterest API v5 only provides refreshable OAuth access tokens'):
            access_token.oauth(refreshable=False)
