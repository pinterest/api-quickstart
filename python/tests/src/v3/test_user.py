import unittest
from unittest import mock

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

    @mock.patch("src.v5.user.ApiObject.get_iterator")
    @mock.patch("src.v5.user.ApiObject.__init__")
    def test_user_get_boards(self, mock_api_object_init, mock_api_object_get_iterator):
        test_user = User("test_user", "test_api_config", "test_access_token")

        mock_api_object_get_iterator.return_value = "test_iterator"
        response = test_user.get_boards(
            {"id": "test_user_id"},
            query_parameters={"param1": "value1", "param2": "value2"},
        )
        mock_api_object_get_iterator.assert_called_once_with(
            "/v3/users/test_user_id/boards/feed/",
            {"param1": "value1", "param2": "value2"},
        )
        self.assertEqual(response, "test_iterator")

        response = test_user.get_boards({"id": "test_user_id2"})
        mock_api_object_get_iterator.assert_called_with(
            "/v3/users/test_user_id2/boards/feed/", None
        )

        response = test_user.get_boards(
            {"id": "test_user_id3"},
            query_parameters={
                "paramA": "valueA",
            },
        )
        mock_api_object_get_iterator.assert_called_with(
            "/v3/users/test_user_id3/boards/feed/", {"paramA": "valueA"}
        )

    @mock.patch("src.v5.user.ApiObject.get_iterator")
    @mock.patch("src.v5.user.ApiObject.__init__")
    def test_user_get_pins(self, mock_api_object_init, mock_api_object_get_iterator):
        test_user = User("test_user", "test_api_config", "test_access_token")

        mock_api_object_get_iterator.return_value = "test_iterator"
        response = test_user.get_pins(
            {"id": "test_user_id"},
            query_parameters={"param3": "value3", "param4": "value4"},
        )
        mock_api_object_get_iterator.assert_called_once_with(
            "/v3/users/test_user_id/pins/", {"param3": "value3", "param4": "value4"}
        )
        self.assertEqual(response, "test_iterator")

        response = test_user.get_pins({"id": "test_user_id2"})
        mock_api_object_get_iterator.assert_called_with(
            "/v3/users/test_user_id2/pins/", None
        )

        response = test_user.get_pins(
            {"id": "test_user_id3"},
            query_parameters={
                "param5": "value5",
            },
        )
        mock_api_object_get_iterator.assert_called_with(
            "/v3/users/test_user_id3/pins/", {"param5": "value5"}
        )
