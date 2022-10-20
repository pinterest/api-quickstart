from analytics_attributes import AdAnalyticsAttributes, AnalyticsAttributes
from api_object import ApiObject

#
# This module uses Pinterest API v5 in three classes:
# * UserAnalytics synchronously retrieves user (organic) reports.
# * PinAnalytics synchronously retrieves pin (organic) reports.
# * AdAnalytics synchronously retrieves advertising reports.
#


class UserAnalytics(AnalyticsAttributes, ApiObject):
    """
    This class retrieves user (sometimes called "organic") metrics
    using the v5 interface.

    The attribute functions are chainable. For example:
       UserAnalytics(user_data.get("id"), api_config, access_token)
       .last_30_days()
       .metrics({"IMPRESSION", "PIN_CLICK_RATE"})

    Note that in v5, the metrics are provided to the API using the
    "columns" parameter, which is encoded as a comma-separated string.

    The AnalyticsAttributes parent class implements parameters that
    are common to all analytics reports.

    The ApiObject parent class implements the REST transaction used
    to fetch the metrics.
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
                    "OWNED_CONTENT",
                    "PIN_FORMAT",
                },
            }
        )

        # chainable attribute setters...

    def from_claimed_content(self, from_claimed_content):
        self.attrs["from_claimed_content"] = from_claimed_content
        return self

    def pin_format(self, pin_format):
        self.attrs["pin_format"] = pin_format
        return self

    def app_types(self, app_types):
        self.attrs["app_types"] = app_types
        return self

    def split_field(self, split_field):
        self.attrs["split_field"] = split_field
        return self

    # https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics
    def get(self, ad_account_id=None):
        """
        Get analytics for the user account. If ad_account_id is set, get user
        analytics associated with the specified Ad Account.
        """
        if ad_account_id:
            self.attrs["ad_account_id"] = ad_account_id
        try:
            return self.request_data(
                "/v5/user_account/analytics?"
                + self.uri_attributes("metric_types", False)
            )
        finally:
            self.attrs.pop("ad_account_id", None)


class PinAnalytics(AnalyticsAttributes, ApiObject):
    """
    This class retrieves pin (also "organic") metrics
    using the v5 interface.

    https://developers.pinterest.com/docs/api/v5/#operation/pins/analytics

    The attribute functions are chainable. For example:
       PinAnalytics(user_id, api_config, access_token)
       .last_30_days()
       .metrics({"IMPRESSION", "PIN_CLICK"})

    The AnalyticsAttributes parent class implements parameters that
    are common to all analytics reports.

    The ApiObject parent class implements the REST transaction used
    to fetch the metrics.
    """

    def __init__(self, pin_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.pin_id = pin_id
        self.enumerated_values.update(
            {
                "app_types": {"all", "mobile", "tablet", "web"},
                "split_field": {
                    "NO_SPLIT",
                    "APP_TYPE",
                },
            }
        )

        # chainable attribute setters...

    def app_types(self, app_types):
        self.attrs["app_types"] = app_types
        return self

    def split_field(self, split_field):
        self.attrs["split_field"] = split_field
        return self

    # https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics
    def get(self, ad_account_id=None):
        """
        Get analytics for the pin. If ad_account_id is set, get pin
        analytics associated with the specified Ad Account.
        """
        if ad_account_id:
            self.attrs["ad_account_id"] = ad_account_id
        try:
            return self.request_data(
                f"/v5/pins/{self.pin_id}/analytics?"
                + self.uri_attributes("metric_types", False)
            )
        finally:
            self.attrs.pop("ad_account_id", None)


class AdAnalytics(AdAnalyticsAttributes, ApiObject):
    """
    This class retrieves advertising delivery metrics with
    Pinterest API version v5.

    The attribute functions are chainable. For example:
       AdAnalytics(api_config, access_token)
       .last_30_days()
       .metrics({"SPEND_IN_DOLLAR", "TOTAL_CLICKTHROUGH"})
       .granularity("DAY")

    The AdAnalyticsAttributes parent class implements parameters that
    are common to all analytics reports.

    The ApiObject parent class implements the REST transaction used
    to fetch the metrics.
    """

    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)
        self.required_attrs.update({"granularity"})
        self.enumerated_values.update(
            # https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
            {"conversion_report_time": {"TIME_OF_AD_ACTION", "TIME_OF_CONVERSION"}}
        )

    def request(self, request_uri):
        """
        Note that the uri_attributes method takes care of encoding the parameters.
        For example, the metrics are sent in the "columns" parameter as a
        comma-separated string.
        """
        return self.request_data(request_uri + self.uri_attributes("columns", True))

    # https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
    def get_ad_account(self, ad_account_id):
        """
        Get analytics for the ad account.
        """
        return self.request(f"/v5/ad_accounts/{ad_account_id}/analytics?")

    # https://developers.pinterest.com/docs/api/v5/#operation/campaigns/analytics
    def get_campaign(self, ad_account_id, campaign_id):
        """
        Get analytics for the campaign.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/campaigns/analytics"
        request_uri += f"?campaign_ids={campaign_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics
    def get_ad_group(self, ad_account_id, _campaign_id, ad_group_id):
        """
        Get analytics for the ad group.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ad_groups/analytics"
        request_uri += f"?ad_group_ids={ad_group_id}&"
        return self.request(request_uri)

    # https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics
    def get_ad(self, ad_account_id, _campaign_id, _ad_group_id, ad_id):
        """
        Get analytics for the ad.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ads/analytics"
        request_uri += f"?ad_ids={ad_id}&"
        return self.request(request_uri)
