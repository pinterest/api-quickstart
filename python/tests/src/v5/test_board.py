import unittest

import mock

from src.v5.board import Board


class BoardTest(unittest.TestCase):
    @mock.patch("src.v5.board.ApiObject.request_data")
    @mock.patch("src.v5.board.ApiObject.__init__")
    def test_board_get(self, mock_api_object_init, mock_api_object_request_data):
        test_board = Board("test_board_id", "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_response"
        response = test_board.get()
        mock_api_object_request_data.assert_called_once_with("/v5/boards/test_board_id")
        self.assertEqual(response, "test_response")

    @mock.patch("src.v5.board.ApiObject.delete_and_check")
    @mock.patch("src.v5.board.ApiObject.get_iterator")
    @mock.patch("src.v5.board.ApiObject.post_data")
    @mock.patch("src.v5.board.ApiObject.__init__")
    def test_board_actions(
        self,
        mock_api_object_init,
        mock_api_object_post_data,
        mock_api_object_get_iterator,
        mock_api_object_delete,
    ):
        test_board = Board(None, "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        # test create
        post_data_return_value = {"id": "new_board_id"}
        mock_api_object_post_data.return_value = post_data_return_value
        new_board_data = {
            "name": "test board name",
            "description": "test description",
            "privacy": "test privacy",
        }
        response = test_board.create(new_board_data)
        self.assertEqual(response, post_data_return_value)
        self.assertEqual(test_board.board_id, "new_board_id")

        # test create_section
        mock_api_object_post_data.return_value = "test_section_create_response"
        test_section_data = {"name": "test section name"}
        response = test_board.create_section(test_section_data)
        self.assertEqual(response, "test_section_create_response")

        mock_api_object_post_data.assert_has_calls(
            [
                mock.call("/v5/boards", new_board_data),
                mock.call("/v5/boards/new_board_id/sections", test_section_data),
            ]
        )

        # test get_pins
        mock_api_object_get_iterator.return_value = "test_iterator"
        response = test_board.get_pins()
        self.assertEqual(response, "test_iterator")

        # test get_sections
        response = test_board.get_sections()
        self.assertEqual(response, "test_iterator")

        # test get_section_pins
        response = test_board.get_section_pins("test_section_id")
        self.assertEqual(response, "test_iterator")

        mock_api_object_get_iterator.assert_has_calls(
            [
                mock.call("/v5/boards/new_board_id/pins"),
                mock.call("/v5/boards/new_board_id/sections"),
                mock.call("/v5/boards/new_board_id/sections/test_section_id/pins"),
            ]
        )

        # test delete
        test_board.delete()
        mock_api_object_delete.assert_called_once_with("/v5/boards/new_board_id")

        # test text_id
        test_text_id = Board.text_id(
            {"owner": {"username": "test_board_username"}, "name": "Test Board Name"}
        )
        self.assertEqual("/test_board_username/test-board-name/", test_text_id)
