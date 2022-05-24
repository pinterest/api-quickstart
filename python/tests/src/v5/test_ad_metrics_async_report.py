import unittest
from unittest import mock

from v5.ad_metrics_async_report import AdMetricsAsyncReport


class AdMetricsAsyncReportTest(unittest.TestCase):
    @mock.patch("ad_metrics_async_report_common.AdMetricsAsyncReportCommon.__init__")
    def test_am_async_report_common(self, amarc_init):
        ad_metrics_async_report = AdMetricsAsyncReport(
            "test_api_config", "test_access_token", "test_advertiser_id"
        )
        self.assertIsInstance(ad_metrics_async_report, AdMetricsAsyncReport)
        amarc_init.assert_called_once_with(
            "test_api_config",
            "test_access_token",
            "/v5/ad_accounts/test_advertiser_id/reports",
        )
