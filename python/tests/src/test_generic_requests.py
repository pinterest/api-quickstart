import unittest
from unittest import mock
from unittest.mock import call

from generic_requests import download_file


class GenericRequestsTest(unittest.TestCase):
    @mock.patch("builtins.open")
    @mock.patch("requests.get")
    def test_downloadfile(self, mock_requests_get, mock_open):
        response = mock.MagicMock()
        response.iter_content.return_value = ["chunk 1", "chunk 2", "chunk 3"]
        response.__enter__.return_value = response  # for context manager
        mock_requests_get.return_value = response

        mock_file = mock.MagicMock()
        mock_file.__enter__.return_value = mock_file  # for context manager

        mock_open.return_value = mock_file
        download_file("test_url", "/test/download/path")
        mock_open.assert_called_once_with("/test/download/path", "wb")

        mock_file.write.assert_has_calls(
            [call("chunk 1"), call("chunk 2"), call("chunk 3")]
        )
