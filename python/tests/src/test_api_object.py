import unittest
import mock
from os.path import dirname, abspath, join
import requests
import requests_mock
import sys

# required for imports in api_object to work
sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_common import SpamException
from api_common import RateLimitException
from api_object import ApiObject

class ApiObjectTest(unittest.TestCase):

    test_uri = 'https://test_host'
    test_path = '/test_path'
    test_uri_path = test_uri + test_path

    @requests_mock.Mocker()
    def test_api_object_v3(self, rm):
        api_config = mock.Mock()
        api_config.api_uri = self.test_uri
        api_config.verbosity = 2
        api_config.version = 'v3'

        access_token = mock.Mock()
        access_token_header = {'access_token_key': 'access_token_value'}
        access_token.header.return_value = access_token_header
        api_object = ApiObject(api_config, access_token)

        rm.get(self.test_uri_path, request_headers=access_token_header,
               json={'data': 'test_get_response_data'})

        response = api_object.request_data(self.test_path)
        self.assertEqual(response, 'test_get_response_data')
        self.assertFalse(rm.last_request.allow_redirects)

        rm.put(self.test_uri_path, request_headers=access_token_header,
               json={'data': 'test_put_response_data'})
        put_data = {'key1': 'value1', 'key2': 'value2'}
        response = api_object.put_data(self.test_path, put_data)
        self.assertEqual(response, 'test_put_response_data')
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual('key1=value1&key2=value2', rm.last_request.text)

        rm.post(self.test_uri_path, request_headers=access_token_header,
                json={'data': 'test_post_response_data'})
        post_data = {'key3': 'value3', 'key4': 'value4'}
        response = api_object.post_data(self.test_path, post_data)
        self.assertEqual(response, 'test_post_response_data')
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(post_data, rm.last_request.json())

        rm.delete(self.test_uri + '/delete_path', request_headers=access_token_header,
                  status_code = 403, reason='test deletion failure',
                  text='should be ignored')
        # verify check called after delete
        with self.assertRaisesRegex(RuntimeError,
                                    'request failed with reason: test deletion failure'):
            api_object.delete_and_check('/delete_path')
        # verify delete called
        self.assertFalse(rm.last_request.allow_redirects)

    @requests_mock.Mocker()
    def test_api_object_v5(self, rm):
        api_config = mock.Mock()
        api_config.api_uri = self.test_uri
        api_config.verbosity = 2
        api_config.version = 'v5'

        access_token = mock.Mock()
        access_token_header = {'access_token_key': 'access_token_value'}
        access_token.header.return_value = access_token_header
        api_object = ApiObject(api_config, access_token)

        expected_response = {'response_key': 'test_get_response_value'}
        rm.get(self.test_uri_path, request_headers=access_token_header,
               json=expected_response)
        response = api_object.request_data(self.test_path)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)

        expected_response = {'response_key': 'test_put_response_value'}
        rm.put(self.test_uri_path, request_headers=access_token_header,
               json=expected_response)
        put_data = {'key5': 'value5', 'key6': 'value6'}
        response = api_object.put_data(self.test_path, put_data)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)
        self.assertEqual('key5=value5&key6=value6', rm.last_request.text)

        expected_response = {'response_key': 'test_post_response_value'}
        rm.post(self.test_uri_path, request_headers=access_token_header,
                json=expected_response)
        response = api_object.post_data(self.test_path)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)
        self.assertEqual(None, rm.last_request.text)


    @requests_mock.Mocker()
    def test_api_object_iterator(self, rm):
        api_config = mock.Mock()
        api_config.api_uri = self.test_uri
        api_config.verbosity = 2
        api_config.version = 'v3'

        access_token = mock.Mock()
        access_token_header = {'access_token_key': 'access_token_value'}
        access_token.header.return_value = access_token_header
        api_object = ApiObject(api_config, access_token)

        rm.get(self.test_uri + '/test_iterpath', headers=access_token_header,
               json={'data': ['one', 'two'], 'bookmark': 'BOOKMARK1'}) # v3 uses data
        rm.get(self.test_uri + '/test_iterpath?bookmark=BOOKMARK1', headers=access_token_header,
               json={'data': ['three']})
        expected_values = ['one', 'two', 'three']
        for index, value in enumerate(api_object.get_iterator('/test_iterpath')):
            self.assertEqual(expected_values[index], value)
        self.assertFalse(rm.last_request.allow_redirects)

        api_config.version = 'v5'
        rm.get(self.test_uri + '/v5_iterpath?key1=value1', headers=access_token_header,
               json={'items': ['rabbit', 'frog'], 'bookmark': 'BOOKMARK2'}) # v5 uses items
        rm.get(self.test_uri + '/v5_iterpath?key1=value1&bookmark=BOOKMARK2', headers=access_token_header,
               json={'data': ['stoat']})
        expected_values = ['rabbit', 'frog', 'stoat']
        for index, value in enumerate(api_object.get_iterator('/v5_iterpath?key1=value1')):
            self.assertEqual(expected_values[index], value)
        self.assertFalse(rm.last_request.allow_redirects)
