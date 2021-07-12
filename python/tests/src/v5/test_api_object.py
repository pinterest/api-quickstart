import unittest
import mock
from os.path import dirname, abspath, join
import sys

# required for imports in api_object to work
sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_common import SpamException
from api_common import RateLimitException
from v5.api_object import ApiObject

class ApiObjectTest(unittest.TestCase):

    @mock.patch('src.v5.api_object.requests.get')
    def test_api_object(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = 'test_response_data'
        mock_requests_get.return_value = mock_response

        api_config = mock.Mock()
        api_config.api_uri = 'test_uri'
        api_config.verbosity = 2

        access_token = mock.Mock()
        access_token.header.return_value = 'test_headers'
        api_object = ApiObject(api_config, access_token)
        response = api_object.request_data('/test_path')
        self.assertEqual(response, 'test_response_data')
        mock_requests_get.assert_called_once_with('test_uri/test_path', headers='test_headers', allow_redirects=False)
