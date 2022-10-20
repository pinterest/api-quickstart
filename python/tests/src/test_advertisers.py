import unittest
from unittest import mock
from unittest.mock import call

from advertisers import Advertisers


class AdvertisersTest(unittest.TestCase):
    @mock.patch("builtins.print")
    @mock.patch("user.ApiObject.get_iterator")
    @mock.patch("user.ApiObject.__init__")
    def test_user_get(self, mock_api_object_init, mock_get_iterator, mock_print):
        test_advertisers = Advertisers(
            "test_user_id", "test_api_uri", "test_access_token"
        )
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_get_iterator.return_value = [
            {"name": "advertiser 1", "id": "advertiser_1_id", "status": "TEST STATUS"},
            {"name": "advertiser 2", "id": "advertiser_2_id"},
        ]
        advertisers_data = test_advertisers.get()

        test_advertisers.print_summary(advertisers_data[1], "Test Summary")
        test_advertisers.print_enumeration(advertisers_data, "Test Kind")
        mock_print.assert_has_calls(
            [
                call("Test Summary ID: advertiser_2_id | Name: advertiser 2"),
                call(
                    "[1] Test Kind ID: advertiser_1_id "
                    "| Name: advertiser 1 (TEST STATUS)"
                ),
                call("[2] Test Kind ID: advertiser_2_id | Name: advertiser 2"),
            ]
        )

        mock_get_iterator.return_value = "test_iterator"
        self.assertEqual(
            "test_iterator",
            test_advertisers.get_campaigns("test_account_id", "query_parameters_1"),
        )
        self.assertEqual(
            "test_iterator",
            test_advertisers.get_ad_groups("test_account_id", "test_campaign_id"),
        )
        self.assertEqual(
            "test_iterator",
            test_advertisers.get_ads(
                "test_account_id",
                "test_campaign_id",
                "test_ad_group_id",
                "query_parameters_3",
            ),
        )
        mock_get_iterator.assert_has_calls(
            [
                call("/v5/ad_accounts", None),
                call("/v5/ad_accounts/test_account_id/campaigns", "query_parameters_1"),
                call(
                    "/v5/ad_accounts/test_account_id/ad_groups"
                    "?campaign_ids=test_campaign_id",
                    None,
                ),
                call(
                    "/v5/ad_accounts/test_account_id/ads"
                    "?campaign_ids=test_campaign_id&ad_group_ids=test_ad_group_id",
                    "query_parameters_3",
                ),
            ]
        )
