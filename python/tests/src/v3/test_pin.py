import json
import unittest
from unittest import mock
from unittest.mock import call

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

    @mock.patch("time.sleep")
    @mock.patch("builtins.print")
    @mock.patch("src.v3.pin.ApiMediaObject.media_to_media_id")
    @mock.patch("src.v3.pin.ApiMediaObject.put_data")
    @mock.patch("src.v3.pin.ApiMediaObject.request_data")
    @mock.patch("src.v3.pin.ApiMediaObject.__init__")
    def test_video_pin_create(
        self,
        mock_api_object_init,
        mock_api_object_request_data,
        mock_api_object_put_data,
        mock_api_object_m2mi,
        mock_print,
        mock_sleep,
    ):
        test_pin = Pin(None, "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_api_object_request_data.side_effect = [
            # first call to create
            {"test_media_id": {"status": "succeeded"}},
            # second call to create
            {"12345": {"status": "failed"}},
            # third call to create
            {"314159265": {"status": "failed", "failure_code": 2718}},
            # fourth call to create
            {"oops_bad_media_id": {"status": "failed", "failure_code": 2718}},
            # fifth call to create
            {"93428665": {"not status": "failed"}},
            # sixth call: seven responses
            {"67890": {"status": "registered"}},
            {"67890": {"status": "processing"}},
            {"67890": {"status": "processing"}},
            {"67890": {"status": "processing"}},
            {"67890": {"status": "processing"}},
            {"67890": {"status": "processing"}},
            {"67890": {"status": "succeeded"}},
        ]

        put_data_return_value = {"id": "new_pin_id"}
        mock_api_object_put_data.return_value = put_data_return_value
        mock_api_object_m2mi.return_value = "test_media_id"
        new_pin_data = {
            "alt_text": "test alt text",
            "description": "test description",
            "link": "test://domain/path1/path2/webpage.html",
            "image_large_url": "test://domain/path1/path2/image.jpg",
        }
        expected_put_data = {
            "board_id": "test_board_id",
            "image_url": new_pin_data["image_large_url"],
            "source_url": new_pin_data["link"],
            "alt_text": new_pin_data["alt_text"],
            "description": new_pin_data["description"],
            "media_upload_id": "test_media_id",
        }

        # first call to create
        response = test_pin.create(new_pin_data, "test_board_id", media="test_media_id")
        self.assertEqual(response, put_data_return_value)
        self.assertEqual(test_pin.pin_id, "new_pin_id")
        mock_api_object_put_data.assert_called_once_with("/v3/pins/", expected_put_data)
        mock_api_object_request_data.assert_called_once_with(
            "/v3/media/uploads/?upload_ids=test_media_id"
        )

        mock_api_object_m2mi.reset_mock()
        mock_api_object_m2mi.return_value = "12345"
        with self.assertRaisesRegex(
            RuntimeError, "upload 12345 failed with code: unknown"
        ):
            # second call results in an exception
            test_pin.create(new_pin_data, "test_board_id", media="file_name")
        mock_api_object_m2mi.assert_called_once_with("file_name")

        mock_api_object_m2mi.return_value = "314159265"
        with self.assertRaisesRegex(
            RuntimeError, "upload 314159265 failed with code: 2718"
        ):
            # third call results in an exception with error code
            test_pin.create(new_pin_data, "test_board_id", media="file_name")

        mock_api_object_m2mi.return_value = "314159265"
        with self.assertRaisesRegex(RuntimeError, "upload 314159265 not found"):
            # fourth call results in an exception due to media id not found
            test_pin.create(new_pin_data, "test_board_id", media="file_name")

        mock_api_object_m2mi.return_value = "93428665"
        with self.assertRaisesRegex(RuntimeError, "upload 93428665 has no status"):
            # fifth call results in an exception due to no status
            test_pin.create(new_pin_data, "test_board_id", media="file_name")

        # sixth call takes some (simulated) time
        mock_api_object_m2mi.return_value = "67890"
        test_pin.create(new_pin_data, "test_board_id", media="test_media_id")
        mock_print.assert_has_calls(
            [
                call("Upload 67890 status: registered. Waiting a second..."),
                call("Upload 67890 status: processing. Waiting 2 seconds..."),
                call("Upload 67890 status: processing. Waiting 4 seconds..."),
                call("Upload 67890 status: processing. Waiting 8 seconds..."),
                call("Upload 67890 status: processing. Waiting 10 seconds..."),
                call("Upload 67890 status: processing. Waiting 10 seconds..."),
            ]
        )
        # check calls to time.sleep()
        mock_sleep.assert_has_calls(
            [call(1), call(2), call(4), call(8), call(10), call(10)]
        )

    @mock.patch("src.v3.pin.ApiMediaObject.upload_file_multipart")
    @mock.patch("src.v3.pin.ApiMediaObject.post_data")
    @mock.patch("src.v3.pin.ApiMediaObject.__init__")
    def test_upload_media(
        self,
        mock_api_object_init,
        mock_api_object_post_data,
        mock_upload_file_multipart,
    ):
        test_pin = Pin(None, "test_api_uri", "test_access_token")

        test_upload_parameters = {
            "key1": "value1",
            "key2": "value2",
        }
        mock_api_object_post_data.return_value = {
            "upload_id": "test_media_id",
            "upload_url": "test_upload_url",
            "upload_parameters": test_upload_parameters,
        }
        media_id = test_pin.upload_media("test_media_path")
        self.assertEqual("test_media_id", media_id)
        mock_api_object_post_data.assert_called_once_with(
            "/v3/media/uploads/register/", {"type": "video"}
        )
        mock_upload_file_multipart.assert_called_once_with(
            "test_upload_url", "test_media_path", test_upload_parameters
        )
