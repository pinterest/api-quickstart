from analytics_attributes import AnalyticsAttributes, AdAnalyticsAttributes
from api_object import ApiObject


class Analytics(AnalyticsAttributes,ApiObject):
    """
    This class retrieves user (sometimes called "organic") metrics
    using the v5 interface.
    """
    def __init__(self, user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user_id = user_id
        self.enumerated_values.update({
            "paid": {0, 1, 2},
            "in_profile": {0, 1, 2},
            "from_owned_content": {0, 1, 2},
            "from_owned_content": {0, 1, 2},
            "downstream": {0, 1, 2},
            "pin_format": {"all", "product", "standard", "standard_product_stl_union",
                           "standard_product_union", "standard_stl_union", "stl", "story",
                           "video"},
            "app_types": {"all", "mobile", "tablet", "web"},
            "publish_types": {"all", "published"},
            "include_curated": {0, 1, 2}
        })

    # https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/v3_analytics_partner_metrics_GET
    def get(self, ad_account_id=None):
        """
        Get analytics for the user account. This method has the ad_account_id
        for symmetry with the v5 interface, but ad_account_id may not be used
        with the v3 or v4 versions of the API.
        """
        if ad_account_id:
            # TODO: confirm this assertion...
            print("User metrics are supported by Pinterest API v5, not v3 or v4.")
            return None
        return self.request_data(f"/v3/partners/analytics/users/{self.user_id}/metrics/?" +
                                 self.uri_attributes("metric_types",False))


class AdAnalytics(AdAnalyticsAttributes,ApiObject):
    """
    This class retrieves advertising delivery metrics with
    Pinterest API version v4, which has essentially the same
    functionality as v5. A separate module (delivery_metrics)
    provides a way to retrieve similar metrics using the v3
    asynchrounous report functionality.
    """
    def __init__(self, _user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.required_attrs.update({"granularity"})
        self.enumerated_values.update({
            "attribution_types": {"INDIVIDUAL", "HOUSEHOLD"}
        })

    def request(self, request_uri):
        return self.request_data(request_uri + self.uri_attributes("columns", True))

    # https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_advertiser_delivery_metrics_handler
    def get_ad_account(self, advertiser_id):
        """
        Get analytics for the ad account.
        """
        return self.request(f"/ads/v4/advertisers/{advertiser_id}/delivery_metrics?")

    # https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_campaign_delivery_metrics_handler
    def get_campaign(self, advertiser_id, campaign_id):
        """
        Get analytics for the campaign.
        """
        request_uri = f"/ads/v4/advertisers/{advertiser_id}/campaigns/delivery_metrics"
        request_uri += f"?campaign_ids={campaign_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ad_group_delivery_metrics_handler
    def get_ad_group(self, advertiser_id, _campaign_id, ad_group_id):
        """
        Get analytics for the ad group.
        """
        request_uri = f"/ads/v4/advertisers/{advertiser_id}/ad_groups/delivery_metrics"
        request_uri += f"?ad_group_ids={ad_group_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ad_delivery_metrics_handler
    def get_ad(self, advertiser_id, _campaign_id, _ad_group_id, ad_id):
        """
        Get analytics for the ad.
        """
        request_uri = f"/ads/v4/advertisers/{advertiser_id}/ads/delivery_metrics"
        request_uri += f"?ad_ids={ad_id}&"
        return self.request(request_uri)
