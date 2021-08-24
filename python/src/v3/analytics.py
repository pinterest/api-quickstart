from analytics_attributes import AdAnalyticsAttributes, AnalyticsAttributes
from api_object import ApiObject

#
# This module uses Pinterest API v3 and v4 in two classes:
# * Analytics synchronously retrieves user (organic) reports.
# * AdAnalytics synchronously retrieves advertising reports.
#


class Analytics(AnalyticsAttributes, ApiObject):
    """
    This class retrieves user (sometimes called "organic") metrics
    using the v5 interface.
    """

    def __init__(self, user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user_id = user_id
        self.enumerated_values.update(
            {
                "paid": {0, 1, 2},
                "in_profile": {0, 1, 2},
                "from_owned_content": {0, 1, 2},
                "downstream": {0, 1, 2},
                "pin_format": {
                    "all",
                    "product",
                    "standard",
                    "standard_product_stl_union",
                    "standard_product_union",
                    "standard_stl_union",
                    "stl",
                    "story",
                    "video",
                },
                "app_types": {"all", "mobile", "tablet", "web"},
                "publish_types": {"all", "published"},
                "include_curated": {0, 1, 2},
            }
        )

    # https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/v3_analytics_partner_metrics_GET
    def get(self, advertiser_id=None):
        """
        Get analytics for the user account. This method has the ad_account_id
        for symmetry with the v5 interface, but ad_account_id may not be used
        with the v3 or v4 versions of the API.
        """
        if advertiser_id:
            print("User account analytics for shared accounts are")
            print("supported by Pinterest API v5, but not v3 or v4.")
            return None
        return self.request_data(
            f"/v3/partners/analytics/users/{self.user_id}/metrics/?"
            + self.uri_attributes("metric_types", False)
        )

    # chainable attribute setters...

    def paid(self, paid):
        self.attrs["paid"] = paid
        return self

    def in_profile(self, in_profile):
        self.attrs["in_profile"] = in_profile
        return self

    def from_owned_content(self, from_owned_content):
        self.attrs["from_owned_content"] = from_owned_content
        return self

    def downstream(self, downstream):
        self.attrs["downstream"] = downstream
        return self

    def pin_format(self, pin_format):
        self.attrs["pin_format"] = pin_format
        return self

    def app_types(self, app_types):
        self.attrs["app_types"] = app_types
        return self

    def publish_types(self, publish_types):
        self.attrs["publish_types"] = publish_types
        return self

    def include_curated(self, include_curated):
        self.attrs["include_curated"] = include_curated
        return self


class AdAnalytics(AdAnalyticsAttributes, ApiObject):
    """
    This class retrieves advertising delivery metrics with
    Pinterest API version v4, which has essentially the same
    functionality as v5. A separate module (delivery_metrics)
    provides a way to retrieve similar metrics using the v3
    asynchronous report functionality.
    """

    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)
        self.required_attrs.update({"granularity"})
        self.enumerated_values.update(
            {"attribution_types": {"INDIVIDUAL", "HOUSEHOLD"}}
        )

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
