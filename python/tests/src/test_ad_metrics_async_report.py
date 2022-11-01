import datetime
import unittest
from unittest import mock

from ad_metrics_async_report import AdMetricsAsyncReport


class AdMetricsAsyncReportTest(unittest.TestCase):
    @mock.patch("async_report.AsyncReport.__init__")
    def test_am_async_report(self, mock_async_report_init):
        am_async_report = (
            AdMetricsAsyncReport(
                "test_api_config", "test_access_token", "test_advertiser_id"
            )
            .start_date("2021-03-01")
            .end_date("2021-03-31")
            .level("PIN_PROMOTION")
            .metrics({"IMPRESSION_1", "CLICKTHROUGH_1"})
            .report_format("JSON")
        )

        mock_async_report_init.assert_called_once_with(
            "test_api_config",
            "test_access_token",
            "/v5/ad_accounts/test_advertiser_id/reports",
        )

        with self.assertRaisesRegex(
            AttributeError, r"missing attributes: .*granularity"
        ):
            am_async_report.post_data_attributes()

        am_async_report.granularity("DAY")

        data_attributes = am_async_report.post_data_attributes()
        self.assertEqual(
            data_attributes,
            {
                "start_date": "2021-03-01",
                "end_date": "2021-03-31",
                "columns": ["CLICKTHROUGH_1", "IMPRESSION_1"],
                "level": "PIN_PROMOTION",
                "granularity": "DAY",
                "report_format": "JSON",
            },
        )

        am_async_report.date_range("2021-03-31", "2021-03-01")  # wrong order
        with self.assertRaisesRegex(ValueError, "start date after end date"):
            am_async_report.post_data_attributes()

    @mock.patch("analytics_attributes.datetime.date", wraps=datetime.date)
    @mock.patch("async_report.AsyncReport.__init__")
    def test_am_async_report_attributes_1(self, mock_async_report_init, mock_date):
        mock_date.today.return_value = datetime.datetime(
            2021, 3, 31
        )  # for call to last_30_days below

        # These attributes might not actually make any sense, but they are
        # valid and test most of the attribute functions.
        am_async_report = (
            AdMetricsAsyncReport(
                "test_api_config", "test_access_token", "test_advertiser_id"
            )
            .last_30_days()
            .level("SEARCH_QUERY")
            .click_window_days(14)
            .conversion_report_time("AD_EVENT")
            .engagement_window_days(7)
            .granularity("HOUR")
            .report_format("CSV")
            .tag_version(3)
            .view_window_days(30)
        )
        # specify metrics with multiple calls
        am_async_report.metrics({"INAPP_SEARCH_ROAS", "INAPP_SEARCH_COST_PER_ACTION"})
        am_async_report.metric("TOTAL_CLICK_SEARCH_QUANTITY")
        am_async_report.metric("TOTAL_CLICK_SEARCH")

        # specify filter
        am_async_report.filters(
            [{"field": "SPEND_IN_DOLLAR", "operator": "GREATER_THAN", "values": [1]}]
        )

        data_attributes = am_async_report.post_data_attributes()
        self.assertEqual(
            data_attributes,
            {
                "start_date": "2021-03-01",
                "end_date": "2021-03-31",
                "columns": [
                    "INAPP_SEARCH_COST_PER_ACTION",
                    "INAPP_SEARCH_ROAS",
                    "TOTAL_CLICK_SEARCH",
                    "TOTAL_CLICK_SEARCH_QUANTITY",
                ],
                "click_window_days": 14,
                "conversion_report_time": "AD_EVENT",
                "engagement_window_days": 7,
                "filters": [
                    {
                        "field": "SPEND_IN_DOLLAR",
                        "operator": "GREATER_THAN",
                        "values": [1],
                    }
                ],
                "granularity": "HOUR",
                "level": "SEARCH_QUERY",
                "report_format": "CSV",
                "tag_version": 3,
                "view_window_days": 30,
            },
        )

    @mock.patch("async_report.AsyncReport.__init__")
    def test_am_async_report_attributes_2(self, mock_async_report_init):
        am_async_report = (
            AdMetricsAsyncReport(
                "test_api_config", "test_access_token", "test_advertiser_id"
            )
            .date_range("2021-03-01", "2021-03-31")
            .level("oops")
            .granularity("MONTH")
            .metrics({"IMPRESSION_1", "CLICKTHROUGH_1"})
        )

        with self.assertRaisesRegex(ValueError, "level: oops is not one of"):
            am_async_report.post_data_attributes()

        am_async_report.level("KEYWORD")
        am_async_report.tag_version(4)

        with self.assertRaisesRegex(ValueError, "tag_version: 4 is not one of"):
            am_async_report.post_data_attributes()
