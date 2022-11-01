class DeliveryMetrics:
    """
    This module will provide access to delivery metrics when it becomes available.
      https://developers.pinterest.com/docs/api/v5/#operation/delivery_metrics/get
    """

    def __init__(self, api_config, access_token):
        pass

    def get(self):
        """
        The full list of all available delivery metrics will be available in v5 soon.
        """
        raise RuntimeError("Metric definitions are not available in API version v5.")
