import unittest
from unittest import mock

from v5.analytics import AdAnalytics, PinAnalytics, UserAnalytics


class UserAnalyticsTest(unittest.TestCase):
    @mock.patch("v5.analytics.ApiObject.request_data")
    @mock.patch("v5.analytics.ApiObject.__init__")
    def test_user_analytics(self, mock_init, mock_request_data):
        analytics = (
            UserAnalytics("test_user_id", "test_api_config", "test_access_token")
            .start_date("2021-03-01")
            .end_date("2021-03-31")
            .metrics({"PIN_CLICK_RATE", "IMPRESSION"})
            .pin_format("regular")
            .from_claimed_content("Both")
        )

        mock_init.assert_called_once_with("test_api_config", "test_access_token")

        mock_request_data.return_value = "test_response"
        self.assertEqual(
            "test_response", analytics.get(ad_account_id="test_ad_account")
        )
        # note that metrics should be sorted
        mock_request_data.assert_called_once_with(
            "/v5/user_account/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK_RATE"
            "&ad_account_id=test_ad_account"
            "&from_claimed_content=Both&pin_format=regular"
        )
        mock_request_data.reset_mock()

        analytics.app_types("web")
        analytics.split_field("PIN_FORMAT")

        # verifies additional parameters and no ad_account_id
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/user_account/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK_RATE"
            "&app_types=web"
            "&from_claimed_content=Both&pin_format=regular"
            "&split_field=PIN_FORMAT"
        )
        mock_request_data.reset_mock()
        # testing with tablet app type
        analytics.app_types("tablet")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/user_account/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK_RATE"
            "&app_types=tablet"
            "&from_claimed_content=Both&pin_format=regular"
            "&split_field=PIN_FORMAT"
        )
        mock_request_data.reset_mock()
        # testing with mobile app type
        analytics.app_types("mobile")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/user_account/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK_RATE"
            "&app_types=mobile"
            "&from_claimed_content=Both&pin_format=regular"
            "&split_field=PIN_FORMAT"
        )
        mock_request_data.reset_mock()
        # testing with all app types
        analytics.app_types("all")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/user_account/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK_RATE"
            "&app_types=all"
            "&from_claimed_content=Both&pin_format=regular"
            "&split_field=PIN_FORMAT"
        )
        mock_request_data.reset_mock()


class PinAnalyticsTest(unittest.TestCase):
    @mock.patch("v5.analytics.ApiObject.request_data")
    @mock.patch("v5.analytics.ApiObject.__init__")
    def test_pin_analytics(self, mock_init, mock_request_data):
        analytics = (
            PinAnalytics("test_user_id", "test_api_config", "test_access_token")
            .start_date("2021-03-01")
            .end_date("2021-03-31")
            .metrics({"PIN_CLICK", "IMPRESSION"})
        )

        mock_init.assert_called_once_with("test_api_config", "test_access_token")

        mock_request_data.return_value = "test_response"
        self.assertEqual(
            "test_response", analytics.get(ad_account_id="test_ad_account")
        )
        # note that metrics should be sorted
        mock_request_data.assert_called_once_with(
            "/v5/pins/test_user_id/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK"
            "&ad_account_id=test_ad_account"
        )
        mock_request_data.reset_mock()

        analytics.app_types("web")
        analytics.split_field("NO_SPLIT")

        # verifies additional parameters and no ad_account_id
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/pins/test_user_id/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK"
            "&app_types=web"
            "&split_field=NO_SPLIT"
        )
        mock_request_data.reset_mock()

        # testing with tablet app type
        analytics.app_types("tablet")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/pins/test_user_id/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK"
            "&app_types=tablet"
            "&split_field=NO_SPLIT"
        )
        mock_request_data.reset_mock()
        # testing with mobile app type
        analytics.app_types("mobile")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/pins/test_user_id/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK"
            "&app_types=mobile"
            "&split_field=NO_SPLIT"
        )
        mock_request_data.reset_mock()
        # testing with all app types
        analytics.app_types("all")
        self.assertEqual("test_response", analytics.get())
        mock_request_data.assert_called_once_with(
            "/v5/pins/test_user_id/analytics?"
            "start_date=2021-03-01&end_date=2021-03-31"
            "&metric_types=IMPRESSION,PIN_CLICK"
            "&app_types=all"
            "&split_field=NO_SPLIT"
        )
        mock_request_data.reset_mock()


class AdAnalyticsTest(unittest.TestCase):
    @mock.patch("v5.analytics.ApiObject.request_data")
    @mock.patch("v5.analytics.ApiObject.__init__")
    def test_adanalytics(self, mock_init, mock_request_data):
        analytics = (
            AdAnalytics("test_api_config", "test_access_token")
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
            "/v5/ad_accounts/test_ad_account/analytics?"
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
            "/v5/ad_accounts/test_ad_account/campaigns/analytics?"
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
            "/v5/ad_accounts/test_ad_account/ad_groups/analytics?"
            "ad_group_ids=test_ad_group"
            "&start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&click_window_days=7"
            "&engagement_window_days=14"
            "&granularity=HOUR"
        )
        mock_request_data.reset_mock()

        analytics.view_window_days(60).conversion_report_time("TIME_OF_CONVERSION")
        self.assertEqual(
            "test_response",
            analytics.get_ad(
                "test_ad_account", "test_campaign", "test_ad_group", "test_ad"
            ),
        )
        mock_request_data.assert_called_once_with(
            "/v5/ad_accounts/test_ad_account/ads/analytics?"
            "ad_ids=test_ad"
            "&start_date=2021-03-01&end_date=2021-03-31"
            "&columns=SPEND_IN_DOLLAR,TOTAL_CLICKTHROUGH"
            "&click_window_days=7"
            "&conversion_report_time=TIME_OF_CONVERSION"
            "&engagement_window_days=14"
            "&granularity=HOUR"
            "&view_window_days=60"
        )
        mock_request_data.reset_mock()
