from ad_metrics_async_report_common import AdMetricsAsyncReportCommon


class AdMetricsAsyncReport(AdMetricsAsyncReportCommon):
    """
    For documentation, see:
    https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report
    """

    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(
            api_config, access_token, f"/v5/ad_accounts/{advertiser_id}/reports"
        )
