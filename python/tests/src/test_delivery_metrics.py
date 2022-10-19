import unittest
from unittest import mock

from v5.delivery_metrics import DeliveryMetrics


class DeliveryMetricsTest(unittest.TestCase):
    @mock.patch("v3.delivery_metrics.ApiObject.__init__")
    def test_delivery_metrics(self, mock_api_object_init):
        test_dm = DeliveryMetrics("test_api_config", "test_access_token")
        mock_api_object_init.assert_not_called()

        with self.assertRaisesRegex(
            RuntimeError, "Metric definitions are not available in API version v5."
        ):
            test_dm.get()
