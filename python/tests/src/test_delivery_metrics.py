import unittest

from delivery_metrics import DeliveryMetrics


class DeliveryMetricsTest(unittest.TestCase):
    def test_delivery_metrics(self):
        test_dm = DeliveryMetrics("test_api_config", "test_access_token")

        with self.assertRaisesRegex(
            RuntimeError, "Metric definitions are not available in API version v5."
        ):
            test_dm.get()
