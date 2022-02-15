import json
import unittest

import mock

from src.v3.pin import Pin


class PinTest(unittest.TestCase):
    @mock.patch("src.v3.pin.ApiMediaObject.request_data")
    @mock.patch("src.v3.pin.ApiMediaObject.__init__")
    def test_pin_get(self, mock_api_object_init, mock_api_object_request_data):
        test_pin = Pin("test_pin_id", "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_response"
        response = test_pin.get()
        mock_api_object_request_data.assert_called_once_with("/v3/pins/test_pin_id/")
        self.assertEqual(response, "test_response")

    @mock.patch("src.v3.pin.ApiMediaObject.put_data")
    @mock.patch("src.v3.pin.ApiMediaObject.request_data")
    @mock.patch("src.v3.pin.ApiMediaObject.__init__")
    def test_pin_create(
        self,
        mock_api_object_init,
        mock_api_object_request_data,
        mock_api_object_put_data,
    ):
        test_pin = Pin(None, "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        put_data_return_value = {"id": "new_pin_id"}
        mock_api_object_put_data.return_value = put_data_return_value
        carousel_data = {
            "carousel_slots": {
                "details": "string",
                "id": "string",
                "images": {"height": 450, "url": "string", "width": 236},
                "link": "string",
                "title": "string",
            },
            "id": "number in a string",
            "index": "another number in a string",
        }
        new_pin_data = {
            "alt_text": "test alt text",
            "description": "test description",
            "link": "test://domain/path1/path2/webpage.html",
            "image_large_url": "test://domain/path1/path2/image.jpg",
            "carousel_data": carousel_data,
        }
        expected_put_data = {
            "board_id": "test_board_id",
            "image_url": new_pin_data["image_large_url"],
            "source_url": new_pin_data["link"],
            "alt_text": new_pin_data["alt_text"],
            "description": new_pin_data["description"],
            "carousel_data_json": json.dumps(carousel_data, separators=(",", ":")),
        }
        response = test_pin.create(new_pin_data, "test_board_id")
        self.assertEqual(response, put_data_return_value)
        self.assertEqual(test_pin.pin_id, "new_pin_id")
        mock_api_object_put_data.assert_called_once_with("/v3/pins/", expected_put_data)
