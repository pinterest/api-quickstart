from ad_metrics_async_report_common import AdMetricsAsyncReportCommon


class AdMetricsAsyncReport(AdMetricsAsyncReportCommon):
    """
    For documentation, see:
    https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler
    """

    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(
            api_config,
            access_token,
            f"/ads/v4/advertisers/{advertiser_id}/delivery_metrics/async",
        )
