import json

from analytics_attributes import AdAnalyticsAttributes

class AdMetricsAsyncReportCommon(AdAnalyticsAttributes):
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
             .report_format('CSV')

    The parent class AdAnalyticsAttributes implements the parameters that
    are shared between synchronous and asynchronous reports.

    The parent class AsyncReport is used to perform the process of requesting
    and waiting for the asynchronous report to be ready.
    """

    def __init__(self, *args):
        super().__init__(*args)  # forward all args to allow multiple inheritance

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
                "report_format": {"CSV", "JSON"},
                "tag_version": {2, 3, "2", "3"},
            }
        )

    def level(self, level):
        """
        Required attribute. Requested report type.
        """
        self.attrs["level"] = level
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

        # TODO: VERIFY WHETHER json.dumps IS STILL NECESSARY
        # self.attrs["filters"] = json.dumps(filters, separators=(",", ":"))
        self.attrs["filters"] = filters
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
