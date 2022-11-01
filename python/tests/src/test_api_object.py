import unittest
from unittest import mock

import requests_mock

from api_object import ApiObject


class ApiObjectTest(unittest.TestCase):
    """
    Tests for the generic ApiObject class that is used for all versions
    of the Pinterest API.

    Note: the reset_backoff and wait_backoff functions are tested with
    the classes that call these functions instead of testing them in
    this file.
    """

    test_uri = "https://test_host"
    test_path = "/test_path"
    test_uri_path = test_uri + test_path

    def test_add_query(self):
        api_object = ApiObject(mock.Mock(), mock.Mock())

        # cases with no parameters to be added
        self.assertEqual("hello", api_object.add_query("hello"))
        self.assertEqual("hello", api_object.add_query("hello", None))
        self.assertEqual("hello", api_object.add_query("hello", {}))

        # verify that different numbers of parameters work
        self.assertEqual(
            "hello?world=ready", api_object.add_query("hello", {"world": "ready"})
        )
        self.assertEqual(
            "hello?world=ready&set=go",
            api_object.add_query("hello", {"world": "ready", "set": "go"}),
        )
        self.assertEqual(
            "hello?world=ready&set=go&eeny=meeny",
            api_object.add_query(
                "hello", {"world": "ready", "set": "go", "eeny": "meeny"}
            ),
        )

        # verify that delimiter works properly when there already
        # parameters in the path
        self.assertEqual(
            "hello?goodbye&cruel=world",
            api_object.add_query("hello?goodbye", {"cruel": "world"}),
        )

        self.assertEqual(
            "hello?good=bye&cruel=world&and=farewell",
            api_object.add_query(
                "hello?good=bye", {"cruel": "world", "and": "farewell"}
            ),
        )

    @requests_mock.Mocker()
    def test_api_object_v5(self, rm):
        api_config = mock.Mock()
        api_config.api_uri = self.test_uri
        api_config.verbosity = 2

        access_token = mock.Mock()
        access_token_header = {"access_token_key": "access_token_value"}
        access_token.header.return_value = access_token_header
        api_object = ApiObject(api_config, access_token)

        expected_response = {"response_key": "test_get_response_value"}
        rm.get(
            self.test_uri_path,
            request_headers=access_token_header,
            json=expected_response,
        )
        response = api_object.request_data(self.test_path)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)

        expected_response = {"response_key": "test_put_response_value"}
        rm.put(
            self.test_uri_path,
            request_headers=access_token_header,
            json=expected_response,
        )
        put_data = {"key5": "value5", "key6": "value6"}
        response = api_object.put_data(self.test_path, put_data)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)
        self.assertEqual("key5=value5&key6=value6", rm.last_request.text)

        expected_response = {"response_key": "test_post_response_value"}
        rm.post(
            self.test_uri_path,
            request_headers=access_token_header,
            json=expected_response,
        )
        response = api_object.post_data(self.test_path)
        self.assertFalse(rm.last_request.allow_redirects)
        self.assertEqual(expected_response, response)
        self.assertEqual(None, rm.last_request.text)

    @requests_mock.Mocker()
    def test_api_object_iterator(self, rm):
        api_config = mock.Mock()
        api_config.api_uri = self.test_uri
        api_config.verbosity = 2

        access_token = mock.Mock()
        access_token_header = {"access_token_key": "access_token_value"}
        access_token.header.return_value = access_token_header
        api_object = ApiObject(api_config, access_token)

        rm.get(
            self.test_uri + "/test_iterpath",
            headers=access_token_header,
            json={"items": ["one", "two"], "bookmark": "BOOKMARK1"},
        )
        rm.get(
            self.test_uri + "/test_iterpath?bookmark=BOOKMARK1",
            headers=access_token_header,
            json={"items": ["three"]},
        )
        expected_values = ["one", "two", "three"]
        for index, value in enumerate(api_object.get_iterator("/test_iterpath")):
            self.assertEqual(expected_values[index], value)
        self.assertFalse(rm.last_request.allow_redirects)
