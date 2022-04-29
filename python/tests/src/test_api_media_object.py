import unittest
from unittest import mock

import requests_mock

from api_media_object import ApiMediaObject


class ApiMediaObjectTest(unittest.TestCase):
    def test_upload_media(self):
        api_media_object = ApiMediaObject(mock.Mock(), mock.Mock())

        with self.assertRaisesRegex(
            RuntimeError, r"upload_media\(\) must be overridden"
        ):
            api_media_object.upload_media("test_media_id")

    @mock.patch("builtins.open")
    def test_media_to_media_id(self, mock_open):
        api_media_object = ApiMediaObject(mock.Mock(), mock.Mock())

        # falsy returns falsy
        self.assertEqual(None, api_media_object.media_to_media_id(None))

        mock_open.side_effect = [
            OSError("open failed. sorry!"),
            mock.MagicMock(),
            OSError("open failed. sorry!"),
        ]

        # media id returns media id
        self.assertEqual("12345", api_media_object.media_to_media_id("12345"))

        # valid file tries to call upload_media
        with self.assertRaisesRegex(
            RuntimeError, r"upload_media\(\) must be overridden"
        ):
            api_media_object.media_to_media_id("test_media_file")

        # invalid media id raises exception
        with self.assertRaisesRegex(ValueError, "invalid media: oops"):
            api_media_object.media_to_media_id("oops")

    @requests_mock.Mocker()
    def test_upload_file_multipart(self, rm):
        api_config = mock.Mock()
        api_config.verbosity = 2
        api_media_object = ApiMediaObject(api_config, mock.Mock())

        test_url = "https://test_upload_host/test_upload_path"
        test_data = {"test_key": "test_value"}
        rm.post(test_url)  # mock the post request

        # mock the upload of a file with the contents "pinteresty video"
        with mock.patch(
            "builtins.open", mock.mock_open(read_data="pinteresty video")
        ) as mock_open:
            api_media_object.upload_file_multipart(test_url, "test_file", test_data)
            mock_open.assert_called_once_with("test_file", "rb")

        # check to verify that the posted form data
        self.assertRegex(
            rm.last_request.text,
            r"Content-Disposition: form-data; "
            r'name="test_key"\r\n\r\n'
            r"test_value\r\n"
            r".*\r\n"
            r'Content-Disposition: form-data; name="file"\r\n\r\n'
            r"pinteresty video",
        )
