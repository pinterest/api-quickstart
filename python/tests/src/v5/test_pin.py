import unittest
from unittest import mock
from unittest.mock import call

from src.v5.pin import Pin


class PinTest(unittest.TestCase):
    @mock.patch("src.v5.pin.ApiMediaObject.request_data")
    @mock.patch("src.v5.pin.ApiMediaObject.__init__")
    def test_pin_get(self, mock_api_object_init, mock_api_object_request_data):
        test_pin = Pin("test_pin_id", "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_api_object_request_data.return_value = "test_response"
        response = test_pin.get()
        mock_api_object_request_data.assert_called_once_with("/v5/pins/test_pin_id")
        self.assertEqual(response, "test_response")

    @mock.patch("src.v5.pin.ApiMediaObject.post_data")
    @mock.patch("src.v5.pin.ApiMediaObject.request_data")
    @mock.patch("src.v5.pin.ApiMediaObject.__init__")
    def test_pin_create(
        self,
        mock_api_object_init,
        mock_api_object_request_data,
        mock_api_object_post_data,
    ):
        test_pin = Pin(None, "test_api_uri", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        post_data_return_value = {"id": "new_pin_id"}
        mock_api_object_post_data.return_value = post_data_return_value
        new_pin_data = {
            "alt_text": "test alt text",
            "description": "test description",
            "link": "test://domain/path1/path2/webpage.html",
            "media": {
                "images": {"originals": {"url": "test://domain/path1/path2/image.jpg"}}
            },
        }
        expected_post_data = {
            "board_id": "test_board_id",
            "media_source": {
                "source_type": "image_url",
                "url": new_pin_data["media"]["images"]["originals"]["url"],
            },
            "link": new_pin_data["link"],
            "alt_text": new_pin_data["alt_text"],
            "description": new_pin_data["description"],
        }
        response = test_pin.create(new_pin_data, "test_board_id")
        self.assertEqual(response, post_data_return_value)
        self.assertEqual(test_pin.pin_id, "new_pin_id")
        mock_api_object_post_data.assert_called_once_with(
            "/v5/pins", expected_post_data
        )

    @mock.patch("time.sleep")
    @mock.patch("builtins.print")
    @mock.patch("src.v5.pin.ApiMediaObject.media_to_media_id")
    @mock.patch("src.v5.pin.ApiMediaObject.post_data")
    @mock.patch("src.v5.pin.ApiMediaObject.request_data")
    @mock.patch("src.v5.pin.ApiMediaObject.__init__")
    def test_video_pin_create(
        self,
        mock_api_object_init,
        mock_api_object_request_data,
        mock_api_object_post_data,
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
            {"status": "succeeded"},
            # second call to create
            {"status": "failed"},
            # third call to create
            {"oops no status": "nothing to see here"},
            # fourth call: seven responses
            {"status": "registered"},
            {"status": "processing"},
            {"status": "processing"},
            {"status": "processing"},
            {"status": "processing"},
            {"status": "processing"},
            {"status": "succeeded"},
        ]

        post_data_return_value = {"id": "new_pin_id"}
        mock_api_object_post_data.return_value = post_data_return_value
        mock_api_object_m2mi.return_value = "test_media_id"
        new_pin_data = {
            "alt_text": "test alt text",
            "description": "test description",
            "link": "test://domain/path1/path2/webpage.html",
            "media": {
                "images": {"originals": {"url": "test://domain/path1/path2/image.jpg"}}
            },
        }
        expected_post_data = {
            "board_id": "test_board_id",
            "media_source": {
                "source_type": "video_id",
                "cover_image_url": new_pin_data["media"]["images"]["originals"]["url"],
                "media_id": "test_media_id",
            },
            "link": new_pin_data["link"],
            "alt_text": new_pin_data["alt_text"],
            "description": new_pin_data["description"],
        }
        # first call to create
        response = test_pin.create(new_pin_data, "test_board_id", media="test_media_id")
        self.assertEqual(response, post_data_return_value)
        self.assertEqual(test_pin.pin_id, "new_pin_id")
        mock_api_object_request_data.assert_called_once_with("/v5/media/test_media_id")
        mock_api_object_post_data.assert_called_once_with(
            "/v5/pins", expected_post_data
        )

        mock_api_object_m2mi.reset_mock()
        mock_api_object_m2mi.return_value = "12345"
        with self.assertRaisesRegex(RuntimeError, "media upload 12345 failed"):
            # second call results in an exception
            test_pin.create(new_pin_data, "test_board_id", media="file_name")
        mock_api_object_m2mi.assert_called_once_with("file_name")

        mock_api_object_m2mi.return_value = "98765432"
        with self.assertRaisesRegex(RuntimeError, "media upload 98765432 not found"):
            # third call results in an exception due to no status
            test_pin.create(new_pin_data, "test_board_id", media="file_name")

        # fourth call takes some (simulated) time
        mock_api_object_m2mi.return_value = "2718"
        response = test_pin.create(new_pin_data, "test_board_id", media="test_media_id")
        mock_print.assert_has_calls(
            [
                call("Media id 2718 status: registered. Waiting a second..."),
                call("Media id 2718 status: processing. Waiting 2 seconds..."),
                call("Media id 2718 status: processing. Waiting 4 seconds..."),
                call("Media id 2718 status: processing. Waiting 8 seconds..."),
                call("Media id 2718 status: processing. Waiting 10 seconds..."),
                call("Media id 2718 status: processing. Waiting 10 seconds..."),
            ]
        )
        # check calls to time.sleep()
        mock_sleep.assert_has_calls(
            [call(1), call(2), call(4), call(8), call(10), call(10)]
        )

    @mock.patch("src.v5.pin.ApiMediaObject.upload_file_multipart")
    @mock.patch("src.v5.pin.ApiMediaObject.post_data")
    @mock.patch("src.v5.pin.ApiMediaObject.__init__")
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
            "media_id": "test_media_id",
            "upload_url": "test_upload_url",
            "upload_parameters": test_upload_parameters,
        }
        media_id = test_pin.upload_media("test_media_path")
        self.assertEqual("test_media_id", media_id)
        mock_api_object_post_data.assert_called_once_with(
            "/v5/media", {"media_type": "video"}
        )
        mock_upload_file_multipart.assert_called_once_with(
            "test_upload_url", "test_media_path", test_upload_parameters
        )
