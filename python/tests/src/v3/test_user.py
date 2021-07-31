import unittest

import mock

from src.v3.user import User


class UserTest(unittest.TestCase):
    @mock.patch("src.v3.user.ApiObject.request_data")
    @mock.patch("src.v3.user.ApiObject.__init__")
    def test_user_get(self, mock_api_object_init, mock_api_object_request_data):
        test_user = User("test_user", "test_api_config", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_response"
        response = test_user.get()
        mock_api_object_request_data.assert_called_once_with("/v3/users/test_user/")
        self.assertEqual(response, "test_response")

    @mock.patch("src.v3.user.ApiObject.request_data")
    @mock.patch("src.v3.user.ApiObject.__init__")
    def test_user_get_businesses(
        self, mock_api_object_init, mock_api_object_request_data
    ):
        test_user = User("test_user", "test_api_config", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_businesses_response"
        response = test_user.get_businesses()
        mock_api_object_request_data.assert_called_once_with(
            "/v3/users/test_user/businesses/"
        )
        self.assertEqual(response, "test_businesses_response")
