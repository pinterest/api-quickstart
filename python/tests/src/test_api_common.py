import unittest

import mock

from api_common import ApiCommon, RateLimitException, SpamException


class ApiCommonTest(unittest.TestCase):
    @mock.patch("builtins.print")
    def test_api_common(self, mock_print):
        mock_api_config = mock.Mock()
        mock_api_config.verbosity = 2

        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        response_json = {"response key": "response value"}
        mock_response.json.return_value = response_json

        api_common = ApiCommon(mock_api_config)

        # verify unpack and printed output for normal response
        unpacked = api_common.unpack(mock_response)
        self.assertEqual(unpacked, response_json)
        mock_print.assert_called_once_with(mock_response)
        mock_print.reset_mock()

        api_common.check(mock_response)  # only side effect should be output
        mock_print.assert_called_once_with(mock_response)
        mock_print.reset_mock()

        # verify request identifier printed at high verbosity
        mock_api_config.verbosity = 3
        mock_response.headers = {"x-pinterest-rid": "test-rid"}
        api_common.check(mock_response)  # only side effect should be output
        mock_print.assert_any_call("x-pinterest-rid:", "test-rid")
        mock_print.reset_mock()

        mock_response.headers = {"x-pinterest-rid": "test-rid2"}
        api_common.unpack(mock_response)
        mock_print.assert_any_call("x-pinterest-rid:", "test-rid2")
        mock_print.reset_mock()

        mock_api_config.verbosity = 2

        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.json.return_value = {"message_detail": "blah blah Spam yada yada"}
        mock_response.headers = {"x-pinterest-rid": "test-rid3"}

        # verify that unpack prints request id on error
        with self.assertRaises(SpamException):
            api_common.unpack(mock_response)

        mock_print.assert_any_call("x-pinterest-rid:", "test-rid3")
        mock_print.reset_mock()

        mock_response.json.return_value = {"other": "something besides a spam response"}

        with self.assertRaises(RateLimitException):
            api_common.unpack(mock_response)

        # verify that check prints request id on error
        mock_response.headers = {"x-pinterest-rid": "test-rid4"}
        with self.assertRaises(RateLimitException):
            api_common.check(mock_response)

        mock_print.assert_any_call("x-pinterest-rid:", "test-rid4")
        mock_print.reset_mock()

        # simulate JSON error thrown by a response with no data
        mock_error_message = "mock error reason"
        mock_response.json.side_effect = RuntimeError(mock_error_message)

        with self.assertRaisesRegex(
            RuntimeError,
            "response does not have valid json content: " + mock_error_message,
        ):
            api_common.unpack(mock_response)

        mock_response.reason = mock_error_message
        mock_response.status_code = 500

        with self.assertRaisesRegex(
            RuntimeError, "request failed with reason: " + mock_error_message
        ):
            api_common.check(mock_response)
