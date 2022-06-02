import unittest
from unittest import mock
from unittest.mock import call

from async_report import AsyncReport


class AsyncReportTest(unittest.TestCase):
    @mock.patch("async_report.ApiObject.request_data")
    @mock.patch("async_report.ApiObject.post_data")
    @mock.patch("async_report.ApiObject.__init__")
    def test_async_report(
        self, mock_api_object_init, mock_post_data, mock_request_data
    ):
        test_async_report = AsyncReport(
            "test_api_config", "test_access_token", "/test/path1"
        )
        self.assertIsInstance(test_async_report, AsyncReport)
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        class TestReport(AsyncReport):
            def __init__(self, api_config, access_token, report_path):
                super().__init__(api_config, access_token, report_path)

        test_report = TestReport("test_api_config", "test_access_token", "/test/path")
        with self.assertRaisesRegex(
            RuntimeError, "subclass must override post_data_attributes()"
        ):
            test_report.request_report()

        class TestReport2(AsyncReport):
            def __init__(self, api_config, access_token, report_path):
                super().__init__(api_config, access_token, report_path)

            def post_data_attributes(self):
                return "test_report2_attributes"

        test_report2 = TestReport2(
            "test_api_config", "test_access_token", "/test/path2"
        )
        mock_post_data.return_value = {"token": "test_report2_token"}
        test_report2.request_report()
        self.assertEqual(test_report2.token, "test_report2_token")
        mock_post_data.assert_called_once_with(
            "/test/path2",
            "test_report2_attributes",
        )

        mock_request_data.return_value = {
            "report_status": "FINISHED",
            "url": "test_report2_url",
        }
        test_report2.wait_report()
        self.assertEqual(test_report2.url(), "test_report2_url")
        mock_request_data.assert_called_once_with(
            "/test/path2?token=test_report2_token"
        )

    @mock.patch("builtins.print")
    @mock.patch("time.sleep")
    @mock.patch("async_report.ApiObject.request_data")
    @mock.patch("async_report.ApiObject.post_data")
    @mock.patch("async_report.ApiObject.__init__")
    def test_async_report_run(
        self,
        mock_api_object_init,
        mock_post_data,
        mock_request_data,
        mock_sleep,
        mock_print,
    ):
        class TestReport3(AsyncReport):
            def __init__(self, api_config, access_token, report_path):
                super().__init__(api_config, access_token, report_path)

            def post_data_attributes(self):
                return "test_report3_attributes"

        test_report3_url = (
            "test_report3_url/x-y-z/metrics_report.txt?Very-long-credentials-string"
        )
        test_report3 = TestReport3(
            "test_api_config", "test_access_token", "/test/path3"
        )
        mock_post_data.return_value = {"token": "test_report3_token"}
        mock_request_data.side_effect = [  # simulate time required to generate the test
            {"report_status": "IN_PROGRESS"},
            {"report_status": "IN_PROGRESS"},
            {"report_status": "IN_PROGRESS"},
            {"report_status": "IN_PROGRESS"},
            {"report_status": "IN_PROGRESS"},
            {"report_status": "IN_PROGRESS"},
            {"report_status": "FINISHED", "url": test_report3_url},
        ]
        test_report3.run()

        # check calls to time.sleep()
        mock_sleep.assert_has_calls(
            [call(1), call(2), call(4), call(8), call(10), call(10)]
        )

        # check calls to print()
        mock_print.assert_has_calls(
            [
                call("Report status: IN_PROGRESS. Waiting a second..."),
                call("Report status: IN_PROGRESS. Waiting 2 seconds..."),
                call("Report status: IN_PROGRESS. Waiting 4 seconds..."),
                call("Report status: IN_PROGRESS. Waiting 8 seconds..."),
                call("Report status: IN_PROGRESS. Waiting 10 seconds..."),
                call("Report status: IN_PROGRESS. Waiting 10 seconds..."),
            ]
        )

        self.assertEqual(test_report3.url(), test_report3_url)  # verify returned URL
        mock_post_data.assert_called_once_with(
            "/test/path3",
            "test_report3_attributes",
        )
        mock_request_data.assert_called_with("/test/path3?token=test_report3_token")
        self.assertEqual(
            test_report3.filename(), "metrics_report.txt"
        )  # verify filename()
