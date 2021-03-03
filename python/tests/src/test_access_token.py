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
        mock_api_config.api_uri = 'test-app-uri'

        mock_response = mock.MagicMock()
        mock_response.__str__.return_value = '<Response [200]>'
        mock_response.text = ('{"status": "test-stats",' +
                              ' "scope": "test-scope",' +
                              ' "access_token": "test-access-token",' +
                              ' "data": {"refresh_token": "test-refresh-token"}' +
                              '}')
        mock_requests_put.return_value = mock_response
        
        access_token = AccessToken(mock_api_config)
        pass
    