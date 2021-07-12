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

    @mock.patch('src.v5.api_object.requests.delete')
    @mock.patch('src.v5.api_object.requests.post')
    @mock.patch('src.v5.api_object.requests.put')
    @mock.patch('src.v5.api_object.requests.get')
    def test_api_object(self, mock_requests_get, mock_requests_put, mock_requests_post, mock_requests_delete):
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

        mock_requests_put.return_value = mock_response
        put_data = {'key1': 'value1', 'key2': 'value2'}
        response = api_object.put_data('/test_path', put_data)
        self.assertEqual(response, 'test_response_data')
        mock_requests_put.assert_called_once_with('test_uri/test_path', data = put_data,
                                                  headers='test_headers', allow_redirects=False)

        mock_requests_post.return_value = mock_response
        post_data = {'key3': 'value3', 'key4': 'value4'}
        response = api_object.post_data('/test_path', post_data)
        self.assertEqual(response, 'test_response_data')
        mock_requests_post.assert_called_once_with('test_uri/test_path', json = post_data,
                                                   headers='test_headers', allow_redirects=False)

        mock_response.ok = False
        mock_response.reason = 'test deletion failure'
        mock_requests_delete.return_value = mock_response
        # verify check called after delete
        with self.assertRaisesRegex(RuntimeError,
                                    'request failed with reason: test deletion failure'):
            api_object.delete_and_check('/delete_path')
        # verify delete called
        mock_requests_delete.assert_called_once_with('test_uri/delete_path',
                                                     headers='test_headers', allow_redirects=False)
