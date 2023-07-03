import unittest
from unittest import mock

from user import User


class UserTest(unittest.TestCase):
    @mock.patch("user.ApiObject.request_data")
    @mock.patch("user.ApiObject.__init__")
    def test_user_get(self, mock_api_object_init, mock_api_object_request_data):
        test_user = User("test_api_config", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_response"
        response = test_user.get()
        mock_api_object_request_data.assert_called_once_with("/v5/user_account")
        self.assertEqual(response, "test_response")

    @mock.patch("user.ApiObject.get_iterator")
    @mock.patch("user.ApiObject.__init__")
    def test_user_get_boards(self, mock_api_object_init, mock_api_object_get_iterator):
        test_user = User("test_api_config", "test_access_token")

        mock_api_object_get_iterator.return_value = "test_iterator"
        response = test_user.get_boards(
            "test_user_data", query_parameters={"param1": "value1", "param2": "value2"}
        )
        mock_api_object_get_iterator.assert_called_once_with(
            "/v5/boards", {"param1": "value1", "param2": "value2"}
        )
        self.assertEqual(response, "test_iterator")

        response = test_user.get_boards("test_user_data")
        mock_api_object_get_iterator.assert_called_with("/v5/boards", None)

        response = test_user.get_boards(
            "test_user_data",
            query_parameters={
                "param1": "value1",
            },
        )
        mock_api_object_get_iterator.assert_called_with(
            "/v5/boards", {"param1": "value1"}
        )

    @mock.patch("user.ApiObject.get_iterator")
    def test_user_get_pins(self, mock_api_object_get_iterator):
        # iterator with three mock boards
        mock_api_object_get_iterator.return_value = iter(
            ["board1_pin1", "board1_pin2", "board3_pin1"]
        )

        mock_api_config = mock.Mock()
        mock_api_config.api_uri = (
            "test_uri"  # just to make underlying ApiObject init work
        )

        # these pins should be returned by the above mock iterator with static data
        expected_pins = ["board1_pin1", "board1_pin2", "board3_pin1"]
        test_user = User(mock_api_config, "test_access_token")
        for index, pin in enumerate(
            test_user.get_pins("test_user_data", query_parameters={"param1": "value1"})
        ):
            self.assertEqual(expected_pins[index], pin)

        mock_api_object_get_iterator.assert_called_once_with(
            "/v5/pins", {"param1": "value1"}
        )
