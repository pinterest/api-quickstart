import unittest
from unittest import mock
from unittest.mock import call

from v3.delivery_metrics import DeliveryMetrics


class DeliveryMetricsTest(unittest.TestCase):
    @mock.patch("builtins.print")
    @mock.patch("v3.user.ApiObject.request_data")
    @mock.patch("v3.delivery_metrics.ApiObject.__init__")
    def test_delivery_metrics(
        self, mock_api_object_init, mock_api_object_request_data, mock_print
    ):
        test_dm = DeliveryMetrics("test_api_config", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        mock_api_object_request_data.return_value = {
            "metrics": [
                {"name": "metric1", "definition": "description 1"},
                {"name": "metric2", "definition": "description 2"},
            ]
        }
        metrics = test_dm.get()
        self.assertEqual(test_dm.summary(metrics[1]), "metric2: description 2")
        test_dm.print_all(metrics)
        mock_print.assert_has_calls(
            [
                call("Available delivery metrics:"),
                call("[1] metric1: description 1"),
                call("[2] metric2: description 2"),
            ]
        )
