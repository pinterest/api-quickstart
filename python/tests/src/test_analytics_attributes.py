import datetime
import unittest
from unittest import mock

from src.v3.analytics import AdAnalyticsAttributes, AnalyticsAttributes


class AnalyticsAttributesTest(unittest.TestCase):
    @mock.patch("src.analytics_attributes.datetime.date", wraps=datetime.date)
    def test_analytics_attributes(self, mock_date):
        attributes = AnalyticsAttributes()
        with self.assertRaisesRegex(AttributeError, "start date not set"):
            attributes.uri_attributes("ignored", False)

        with self.assertRaisesRegex(AttributeError, "start date not set"):
            attributes.data_attributes("ignored", False)

        attributes.start_date("oops")
        with self.assertRaisesRegex(
            ValueError, "start_date: oops needs to be a UTC date in YYYY-MM-DD format"
        ):
            attributes.uri_attributes("ignored", False)

        attributes.start_date("2021-05-01")
        with self.assertRaisesRegex(AttributeError, "end date not set"):
            attributes.uri_attributes("ignored", False)

        attributes.end_date("oops")
        with self.assertRaisesRegex(
            ValueError, "end_date: oops needs to be a UTC date in YYYY-MM-DD format"
        ):
            attributes.uri_attributes("ignored", False)

        attributes.date_range("2021-05-31", "2021-05-01")
        with self.assertRaisesRegex(ValueError, "start date after end date"):
            attributes.uri_attributes("ignored", True)

        mock_date.today.return_value = datetime.datetime(
            2021, 5, 31
        )  # for call to last_30_days below
        attributes.last_30_days()

        self.assertEqual(
            attributes.uri_attributes("ignored", False),
            "start_date=2021-05-01&end_date=2021-05-31",
        )

        self.assertEqual(
            attributes.data_attributes("ignored", False),
            {
                "start_date": "2021-05-01",
                "end_date": "2021-05-31",
            },
        )

        with self.assertRaisesRegex(AttributeError, "metrics not set"):
            attributes.uri_attributes("ignored", True)

        attributes.metric("METRIC_2").metrics({"METRIC_3", "METRIC_1"})
        self.assertEqual(
            attributes.uri_attributes("statistics", False),
            "start_date=2021-05-01&end_date=2021-05-31"
            "&statistics=METRIC_1,METRIC_2,METRIC_3",
        )

        attributes.required_attrs.update({"required_one", "required_two"})

        # order is not guaranteed in the set
        with self.assertRaisesRegex(
            AttributeError, r"missing attributes: \['required_one', 'required_two'\]"
        ):
            attributes.uri_attributes("ignored", False)

        attributes.attrs["required_one"] = "value_one"
        attributes.attrs["required_two"] = "value_two"
        self.assertEqual(
            attributes.uri_attributes("statistics", False),
            "start_date=2021-05-01&end_date=2021-05-31"
            "&statistics=METRIC_1,METRIC_2,METRIC_3"
            "&required_one=value_one&required_two=value_two",
        )

        attributes.enumerated_values.update(
            {
                "fibonacci": {1, 2, 3, 5, 8},
            }
        )

        attributes.attrs["fibonacci"] = 4
        with self.assertRaisesRegex(
            ValueError, r"fibonacci: 4 is not one of \[1, 2, 3, 5, 8\]"
        ):
            attributes.uri_attributes("ignored", False)

        attributes.enumerated_values.update({"animal": {"cat", "dog", "fish"}})

        attributes.attrs["fibonacci"] = 5
        attributes.attrs["animal"] = "dog"  # of course, if you have to pick just one
        self.assertEqual(
            attributes.uri_attributes("statistics", False),
            "start_date=2021-05-01&end_date=2021-05-31"
            "&statistics=METRIC_1,METRIC_2,METRIC_3"
            "&animal=dog&fibonacci=5"
            "&required_one=value_one&required_two=value_two",
        )

        self.assertEqual(
            attributes.data_attributes("columns", True),
            {
                "start_date": "2021-05-01",
                "end_date": "2021-05-31",
                "columns": ["METRIC_1", "METRIC_2", "METRIC_3"],
                "animal": "dog",
                "fibonacci": 5,
                "required_one": "value_one",
                "required_two": "value_two",
            },
        )


class AdAnalyticsAttributesTest(unittest.TestCase):
    def test_ad_analytics_attributes(self):
        attributes = (
            AdAnalyticsAttributes()
            .date_range("2021-05-01", "2021-05-31")
            .granularity("MONTH")
            .click_window_days(1)
            .engagement_window_days(7)
            .view_window_days(14)
            .conversion_report_time("CONVERSION_EVENT")
        )

        self.assertEqual(
            attributes.uri_attributes("ignored", False),
            "start_date=2021-05-01&end_date=2021-05-31"
            "&click_window_days=1"
            "&conversion_report_time=CONVERSION_EVENT"
            "&engagement_window_days=7"
            "&granularity=MONTH"
            "&view_window_days=14",
        )

        attributes.click_window_days(42)
        with self.assertRaisesRegex(
            ValueError, r"click_window_days: 42 is not one of \[0, 1, 7, 14, 30, 60\]"
        ):
            attributes.uri_attributes("ignored", False)
