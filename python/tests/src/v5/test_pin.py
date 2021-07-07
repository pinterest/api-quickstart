import unittest
import mock
from src.v5.pin import Pin

class PinTest(unittest.TestCase):
    @mock.patch('src.v5.pin.ApiObject.request_data')
    @mock.patch('src.v5.pin.ApiObject.__init__')
    def test_pin_get(self, mock_api_object_init, mock_api_object_request_data):
        test_pin = Pin('test_pin_id', 'test_api_uri', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_uri', 'test_access_token')

        mock_api_object_request_data.return_value = 'test_response'
        response = test_pin.get()
        mock_api_object_request_data.assert_called_once_with('/v5/pins/test_pin_id')
        self.assertEqual(response, 'test_response')

    @mock.patch('src.v5.pin.ApiObject.post_data')
    @mock.patch('src.v5.pin.ApiObject.request_data')
    @mock.patch('src.v5.pin.ApiObject.__init__')
    def test_pin_create(self, mock_api_object_init, mock_api_object_request_data, mock_api_object_post_data):
        test_pin = Pin(None, 'test_api_uri', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_uri', 'test_access_token')

        post_data_return_value = {'id': 'new_pin_id'}
        mock_api_object_post_data.return_value = post_data_return_value
        new_pin_data = {
            'alt_text': 'test alt text',
            'description': 'test description',
            'link': 'test://domain/path1/path2/webpage.html',
            'media': {'images': {'originals': {'url': 'test://domain/path1/path2/image.jpg'}}}
        }
        expected_post_data = {
            'board_id': 'test_board_id',
            'media_source': {'source_type': 'image_url',
                             'url': new_pin_data['media']['images']['originals']['url']},
            'link': new_pin_data['link'],
            'alt_text': new_pin_data['alt_text'],
            'description': new_pin_data['description']
        }
        response = test_pin.create(new_pin_data, 'test_board_id')
        self.assertEqual(response, post_data_return_value)
        self.assertEqual(test_pin.pin_id, 'new_pin_id')
        mock_api_object_post_data.assert_called_once_with('/v5/pins', expected_post_data)
