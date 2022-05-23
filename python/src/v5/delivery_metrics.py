from api_object import ApiObject

class DeliveryMetrics(ApiObject):
    """
    This class provides a compatible interface for an endpoint
    that exists in v3 but not v5.
    """

    # TODO: Is a null constructor required?
    def __init__(self, api_config, access_token):
        pass

    def get(self):
        """
        The full list of all available delivery metrics is available in v3 but not v5.
        """
        raise RuntimeError("Metric definitions are not available in API version v5.")
