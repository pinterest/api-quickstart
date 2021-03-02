import unittest
import mock
from src.api_object import ApiObject

class ApiObjectTest(unittest.TestCase):

    @mock.patch('src.api_object.requests.get')
    def test_api_object(self, mock_requests_get):
        response = mock.Mock()
        response.ok = True
        response.text = '{"data":"test_response_data"}'
        mock_requests_get.return_value = response

        api_config = mock.Mock()
        api_config.api_uri = 'test_uri'

        access_token = mock.Mock()
        access_token.header.return_value = 'test_headers'
        api_object = ApiObject(api_config, access_token)
        response = api_object.request_data('/test_path')
        self.assertEqual(response, 'test_response_data')
        mock_requests_get.assert_called_once_with('test_uri/test_path', headers='test_headers')
