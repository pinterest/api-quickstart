import unittest

import mock

from src.v3.analytics import AdAnalytics, Analytics


class AnalyticsTest(unittest.TestCase):
    @mock.patch("src.v3.analytics.ApiObject.request_data")
    @mock.patch("src.v3.analytics.ApiObject.__init__")
    def test_analytics(self, mock_init, mock_request_data):
        analytics = (
            Analytics("test_user_id", "test_api_config", "test_access_token")
            .start_date("2021-03-01")
            .end_date("2021-03-31")
            .metrics({"TOTAL_CLICKTHROUGH", "SPEND_IN_DOLLAR"})
            .paid(1)
            .in_profile(2)
        )

        mock_init.assert_called_once_with("test_api_config", "test_access_token")

        mock_request_data.return_value = "test_response"

        self.assertEqual("test_response", analytics.get())
        # note that metrics should be sorted
        mock_request_data.assert_called_once_with(
            "/v3/partners/analytics/users/test_user_id/metrics/?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&in_profile=2&paid=1"
        )
        mock_request_data.reset_mock()

        analytics.downstream(0).pin_format("product").app_types("tablet").publish_types(
            "published"
        ).include_curated(2)

        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v3/partners/analytics/users/test_user_id/metrics/?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&app_types=tablet&downstream=0"
            "&in_profile=2&include_curated=2&paid=1"
            "&pin_format=product&publish_types=published"
        )
        mock_request_data.reset_mock()

        # v3/v4 metrics do not work with advertiser id
        self.assertEqual(None, analytics.get("test_advertiser_id"))
        mock_request_data.assert_not_called()

        analytics.downstream("not_valid")
        with self.assertRaisesRegex(
            ValueError, r"downstream: not_valid is not one of \[0, 1, 2\]"
        ):
            analytics.get()


class AdAnalyticsTest(unittest.TestCase):
    @mock.patch("src.v5.analytics.ApiObject.request_data")
    @mock.patch("src.v5.analytics.ApiObject.__init__")
    def test_adanalytics(self, mock_init, mock_request_data):
        analytics = (
            AdAnalytics("test_user_id", "test_api_config", "test_access_token")
            .start_date("2021-03-01")
            .end_date("2021-03-31")
        )

        mock_init.assert_called_once_with("test_api_config", "test_access_token")

        with self.assertRaisesRegex(
            AttributeError, r"missing attributes: \['granularity'\]"
        ):
            analytics.get_ad_account("should_not_be_used")

        analytics.granularity("DAY")

        with self.assertRaisesRegex(AttributeError, "metrics not set"):
            analytics.get_ad_account("should_not_be_used")

        analytics.metrics({"TOTAL_CLICKTHROUGH", "SPEND_IN_DOLLAR"})

        mock_request_data.return_value = "test_response"
        self.assertEqual("test_response", analytics.get_ad_account("test_ad_account"))
        # note that metrics should be sorted
        mock_request_data.assert_called_once_with(
            "/ads/v4/advertisers/test_ad_account/delivery_metrics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&granularity=DAY"
        )
        mock_request_data.reset_mock()

        analytics.click_window_days(7)
        self.assertEqual(
            "test_response", analytics.get_campaign("test_ad_account", "test_campaign")
        )
        mock_request_data.assert_called_once_with(
            "/ads/v4/advertisers/test_ad_account/campaigns/delivery_metrics?"
            "campaign_ids=test_campaign"
            "&start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&click_window_days=7"
            "&granularity=DAY"
        )
        mock_request_data.reset_mock()

        analytics.engagement_window_days(14).granularity("HOUR")
        self.assertEqual(
            "test_response",
            analytics.get_ad_group("test_ad_account", "test_campaign", "test_ad_group"),
        )
        mock_request_data.assert_called_once_with(
            "/ads/v4/advertisers/test_ad_account/ad_groups/delivery_metrics?"
            "ad_group_ids=test_ad_group"
            "&start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&click_window_days=7"
            "&engagement_window_days=14"
            "&granularity=HOUR"
        )
        mock_request_data.reset_mock()

        analytics.view_window_days(60).conversion_report_time("AD_EVENT")
        self.assertEqual(
            "test_response",
            analytics.get_ad(
                "test_ad_account", "test_campaign", "test_ad_group", "test_ad"
            ),
        )
        mock_request_data.assert_called_once_with(
            "/ads/v4/advertisers/test_ad_account/ads/delivery_metrics?"
            "ad_ids=test_ad"
            "&start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&click_window_days=7"
            "&conversion_report_time=AD_EVENT"
            "&engagement_window_days=14"
            "&granularity=HOUR"
            "&view_window_days=60"
        )
        mock_request_data.reset_mock()
