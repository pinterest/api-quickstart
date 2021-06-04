import unittest
import mock
from src.v3.board import Board

class BoardTest(unittest.TestCase):
    @mock.patch('src.v3.board.ApiObject.request_data')
    @mock.patch('src.v3.board.ApiObject.__init__')
    def test_board_get(self, mock_api_object_init, mock_api_object_request_data):
        test_board = Board('test_board_id', 'test_api_uri', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_uri', 'test_access_token')

        mock_api_object_request_data.return_value = 'test_response'
        response = test_board.get()
        mock_api_object_request_data.assert_called_once_with('/v3/boards/test_board_id/')
        self.assertEqual(response, 'test_response')

    @mock.patch('src.v3.board.ApiObject.put_data')
    @mock.patch('src.v3.board.ApiObject.request_data')
    @mock.patch('src.v3.board.ApiObject.__init__')
    def test_board_create(self, mock_api_object_init, mock_api_object_request_data, mock_api_object_put_data):
        test_board = Board(None, 'test_api_uri', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_uri', 'test_access_token')

        put_data_return_value = {'id': 'new_board_id'}
        mock_api_object_put_data.return_value = put_data_return_value
        new_board_data = {
            'name': 'test board name',
            'category': 'test category',
            'description': 'test description',
        }
        response = test_board.create(new_board_data)
        self.assertEqual(response, put_data_return_value)
        self.assertEqual(test_board.board_id, 'new_board_id')
        mock_api_object_put_data.assert_called_once_with('/v3/boards/', new_board_data)
