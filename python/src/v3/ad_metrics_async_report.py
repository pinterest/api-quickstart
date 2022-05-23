from ad_metrics_async_report_common import AdMetricsAsyncReportCommon
from async_report import AsyncReport

# The unit tests mock AsyncReport, so the first parent needs to be
# AdMetricsAsyncReportCommon to make the multiple inheritance work correctly.
# In particular, if AdMetricsAsyncReportCommon is not first in the order,
# the __init__ functions aren't called correctly.
class AdMetricsAsyncReport(AdMetricsAsyncReportCommon, AsyncReport):
    """
    For documentation, see:
    https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler

    The parent class AdMetricsAsyncReportCommon implements the parameters that
    are shared between different API version reports.

    The parent class AsyncReport is used to perform the process of requesting
    and waiting for the asynchronous report to be ready.
    """

    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(
            api_config,
            access_token,
            f"/ads/v4/advertisers/{advertiser_id}/delivery_metrics/async"
        )
