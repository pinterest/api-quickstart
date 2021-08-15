from analytics_attributes import AdAnalyticsAttributes, AnalyticsAttributes
from api_object import ApiObject


class Analytics(AnalyticsAttributes, ApiObject):
    """
    This class retrieves user (sometimes called "organic") metrics
    using the v5 interface.
    """

    def __init__(self, _user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.enumerated_values.update(
            {
                "from_claimed_content": {"Other", "Claimed", "Both"},
                "pin_format": {"all", "product", "regular", "video"},
                "app_types": {"all", "mobile", "tablet", "web"},
                "split_field": {
                    "NO_SPLIT",
                    "APP_TYPE",
                    "CONTENT_TYPE",
                    "OWNED_CONTENT",
                    "SOURCE",
                    "PIN_FORMAT_CONVERSION_TYPE",
                    "ATTRIBUTION_EVENT",
                },
            }
        )

    # https://developers.pinterest.com/docs/v5/#operation/account/analytics
    def get(self, ad_account_id=None):
        """
        Get analytics for the user account. If ad_account_id is set, get user
        analytics associated with the specified Ad Account.
        """
        if ad_account_id:
            self.attrs["ad_account_id"] = ad_account_id
        return self.request_data(
            "/v5/user_account/analytics?" + self.uri_attributes("metric_types", False)
        )


class AdAnalytics(AdAnalyticsAttributes, ApiObject):
    """
    This class retrieves advertising delivery metrics with
    Pinterest API version v5.
    """

    def __init__(self, _user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.required_attrs.update({"granularity"})

    def request(self, request_uri):
        return self.request_data(request_uri + self.uri_attributes("columns", True))

    # https://developers.pinterest.com/docs/v5/#operation/advertisers/analytics
    def get_ad_account(self, ad_account_id):
        """
        Get analytics for the ad account.
        """
        return self.request(f"/v5/ad_accounts/{ad_account_id}/analytics?")

    # https://developers.pinterest.com/docs/v5/#operation/campaigns/analytics
    def get_campaign(self, ad_account_id, campaign_id):
        """
        Get analytics for the campaign.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/campaigns/analytics"
        request_uri += f"?campaign_ids={campaign_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/v5/#operation/ad_groups/analytics
    def get_ad_group(self, ad_account_id, _campaign_id, ad_group_id):
        """
        Get analytics for the ad group.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ad_groups/analytics"
        request_uri += f"?ad_group_ids={ad_group_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/v5/#operation/ads/analytics
    def get_ad(self, ad_account_id, _campaign_id, _ad_group_id, ad_id):
        """
        Get analytics for the ad.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ads/analytics"
        request_uri += f"?ad_ids={ad_id}&"
        return self.request(request_uri)
