import unittest

import mock
from mock import call

from src.v3.advertisers import Advertisers


class AdvertisersTest(unittest.TestCase):
    @mock.patch("builtins.print")
    @mock.patch("src.v3.user.ApiObject.get_iterator")
    @mock.patch("src.v3.user.ApiObject.request_data")
    @mock.patch("src.v3.user.ApiObject.__init__")
    def test_user_get(
        self, mock_api_object_init, mock_request_data, mock_get_iterator, mock_print
    ):
        test_advertisers = Advertisers(
            "test_user_id", "test_api_uri", "test_access_token"
        )
        mock_api_object_init.assert_called_once_with(
            "test_api_uri", "test_access_token"
        )

        mock_request_data.return_value = [
            {"name": "advertiser 1", "id": "advertiser_1_id", "status": "TEST STATUS"},
            {"name": "advertiser 2", "id": "advertiser_2_id"},
        ]
        advertisers_data = test_advertisers.get()
        mock_request_data.assert_called_once_with(
            "/ads/v3/advertisers/?owner_user_id=test_user_id&include_acl=true"
        )

        test_advertisers.print_summary(advertisers_data[1], 'Test Summary')
        test_advertisers.print_enumeration(advertisers_data, 'Test Kind')
        mock_print.assert_has_calls(
            [
                call("Test Summary ID: advertiser_2_id | Name: advertiser 2"),
                call("[1] Test Kind ID: advertiser_1_id | Name: advertiser 1 (TEST STATUS)"),
                call("[2] Test Kind ID: advertiser_2_id | Name: advertiser 2"),
            ]
        )

        mock_get_iterator.return_value = "test_iterator"
        self.assertEqual("test_iterator", test_advertisers.get_campaigns("test_account_id"))
        self.assertEqual("test_iterator", test_advertisers.get_ad_groups(None, "test_campaign_id"))
        self.assertEqual("test_iterator", test_advertisers.get_ads(None, None, "test_ad_group_id"))
        mock_get_iterator.assert_has_calls(
            [
                call("/ads/v3/advertisers/test_account_id/campaigns/"),
                call("/ads/v3/campaigns/test_campaign_id/ad_groups/"),
                call("/ads/v3/ad_groups/test_ad_group_id/pin_promotions/")
            ]
        )
