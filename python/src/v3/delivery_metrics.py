import json

from analytics_attributes import AdAnalyticsAttributes
from api_object import ApiObject
from v3.async_report import AsyncReport

#
# This module has two classes:
# * DeliveryMetrics retrieves the complete list of metrics
#   available for advertising delivery analytics.
# * DeliveryMetricsAsyncReport sets up and retrieves a
#   metrics report asynchronously.
#


class DeliveryMetrics(ApiObject):
    """
    Use this class to get and to print all of the available
    advertising delivery metrics.
    """

    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_delivery_metrics_handler_GET
    def get(self):
        """
        Get the full list of all available delivery metrics.
        This call is not used much in day-to-day API code, but is a useful endpoint
        for learning about the metrics.
        """
        return self.request_data("/ads/v4/resources/delivery_metrics").get("metrics")

    def summary(self, delivery_metric):
        return f"{delivery_metric['name']}: {delivery_metric['definition']}"

    def print(self, delivery_metric):
        """
        Print summary of a single metric.
        """
        print(self.summary(delivery_metric))

    def print_all(self, delivery_metrics):
        """
        Print summary of data returned by get().
        """
        print("Available delivery metrics:")
        for idx, metric in enumerate(delivery_metrics):
            print(f"[{idx + 1}] " + self.summary(metric))


# The unit tests mock AsyncReport, so the first parent needs to be
# AdAnalyticsAttributes to make the multiple inheritance work correctly.
# In particular, if AdAnalyticsAttributes is not first in the order,
# the __init__ functions aren't called correctly.
class DeliveryMetricsAsyncReport(AdAnalyticsAttributes, AsyncReport):
    """
    Specifies all of the attributes for the async advertiser
    delivery metrics report. For more information, see:
    https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler

    The attribute functions are chainable. For example:
    report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
             .start_date('2021-03-01') \
             .end_date('2021-03-31') \
             .level('PIN_PROMOTION') \
             .granularity('DAY') \
             .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'}) \
             .report_format('csv')

    The parent class AdAnalyticsAttributes implements the parameters that
    are shared between synchronous and asynchronous reports.

    The parent class AsyncReport is used to perform the process of requesting
    and waiting for the asynchronous report to be ready.
    """

    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token, advertiser_id)
        self.kind_of = "delivery_metrics"  # override required by superclass

        # set required attributes
        self.required_attrs.add("level")
        self.required_attrs.add("granularity")

        # This dictionary lists values for attributes that are enumerated
        # in the API documentation. The keys are the names of the attributes,
        # and the dictionary values are sets of API-defined values.
        self.enumerated_values.update(
            {
                "data_source": {"OFFLINE", "REALTIME"},
                "entity_fields": {
                    "AD_GROUP_ID",
                    "AD_GROUP_NAME",
                    "AD_GROUP_STATUS",
                    "CAMPAIGN_ID",
                    "CAMPAIGN_MANAGED_STATUS",
                    "CAMPAIGN_NAME",
                    "CAMPAIGN_STATUS",
                    "PIN_PROMOTION_ID",
                    "PIN_PROMOTION_NAME",
                    "PIN_PROMOTION_STATUS",
                    "PRODUCT_GROUP_ID",
                },
                "level": {
                    "ADVERTISER",
                    "AD_GROUP",
                    "CAMPAIGN",
                    "ITEM",
                    "KEYWORD",
                    "PIN_PROMOTION",
                    "PIN_PROMOTION_TARGETING",
                    "PRODUCT_GROUP",
                    "PRODUCT_GROUP_TARGETING",
                    "PRODUCT_ITEM",
                    "SEARCH_QUERY",
                },
                "report_format": {"csv", "json"},
                "tag_version": {2, 3, "2", "3"},
            }
        )

    def level(self, level):
        """
        Required attribute. Requested report type.
        """
        self.attrs["level"] = level
        return self

    def data_source(self, data_source):
        """
        Either OFFLINE or REALTIME. Offline metrics have a long retention and are
        used for billing (source of truth). Realtime metrics have latest metrics
        (including today) but only have a 72-hour retention. In addition, realtime
        metrics are expected to be an estimation and could be slightly inaccurate.
        Please note that only a limited set of metrics are available for realtime data.
        """
        self.attrs["data_source"] = data_source
        return self

    def entity_fields(self, entity_fields):
        """
        Additional fields that you would like included for each entity in the
        Delivery Metrics Report. Fields will be prefixed with the requested level
        when returned in the report, for example if CAMPAIGN_ID is requested at the
        AD_GROUP level, this field will be called AD_GROUP_CAMPAIGN_ID.
        Please note that entity fields can only be requested for the specified level
        and its parents, for example, for an AD_GROUP level request CAMPAIGN and
        AD_GROUP entity_fields can be requested, but PIN_PROMOTION entity_fields
        cannot.
        """
        self.attrs["entity_fields"] = entity_fields
        return self

    def filters(self, filters):
        """
        Filters must be a list of structures with fields as specified by the API.
        JSON separators are set to eliminate whitespace and to get the most
        compact JSON representation.
        """
        self.attrs["filters"] = json.dumps(filters, separators=(",", ":"))
        return self

    def report_format(self, report_format):
        """
        Specification for formatting report data.
        """
        self.attrs["report_format"] = report_format
        return self

    def tag_version(self, tag_version):
        """
        By default, Pinterest Tag metrics are returned. To view metrics
        from prior conversion tags, set this field to 2.
        """
        self.attrs["tag_version"] = tag_version
        return self

    def post_data_attributes(self):
        """
        This override is required by the superclass AsyncReport.
        """
        return self.data_attributes("columns", True)  # metrics are required
