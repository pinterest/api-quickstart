from api_object import ApiObject


class DeliveryMetrics(ApiObject):
    """
    Use this class to get and to print all of the available
    advertising delivery metrics.
    """

    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    def get(self):
        """
        https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_available_metrics_definition_handler
        Get the full list of all available delivery metrics.
        This call is not used much in day-to-day API code, but is a useful endpoint
        for learning about the metrics.
        """  # noqa: E501 because the long URL is okay
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
