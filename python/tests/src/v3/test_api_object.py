import unittest
import mock
from os.path import dirname, abspath, join
import sys

# required for imports in api_object to work
sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_common import SpamException
from api_common import RateLimitException
from v3.api_object import ApiObject

class ApiObjectTest(unittest.TestCase):

    @mock.patch('src.v3.api_object.requests.get')
    def test_api_object(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'data': 'test_response_data'}
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

        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.reason = 'Too Many Requests'
        mock_response.json.return_value = {'message_detail': 'blah blah Spam yada yada'}

        with self.assertRaises(SpamException):
            api_object.request_data('/test_path/spammy-thing')

        mock_response.json.return_value = {'other': 'something besides a spam response'}

        with self.assertRaises(RateLimitException):
            api_object.request_data('/test_path/oops-rate-limit')

        # simulate JSON error thrown by a response with no data
        mock_error_message = 'mock error reason'
        mock_response.json.side_effect = RuntimeError(mock_error_message)

        with self.assertRaisesRegex(RuntimeError,
                                    'response does not have valid json content: ' +
                                    mock_error_message):
            api_object.request_data('/test_path/oops-bad-json')
