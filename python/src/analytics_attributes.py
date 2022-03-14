import datetime

#
# The two classes in this module (AnalyticsAttributes and AdAnalyticsAttributes)
# provide common parameters for API v3, v4, and v5 synchronous and asynchronous
# reports. AnalyticsAttributes implements parameters that are common to all
# reports; AdAnalyticsAttributes extents AnalyticsAttributes to implement
# parameters for all advertising reports.
#
# Class Diagram (the arrow indicates a parent->child relationship)
#    AnalyticsAttributes
#    -> Analytics(v3)
#    -> Analytics(v5)
#    -> AdAnalyticsAttributes
#       -> AdAnalytics(v3/v4)
#       -> AdAnalytics(v5)
#       -> DeliveryMetricsAsyncReport(v3 only)
#


class AnalyticsAttributes:
    """
    This class profiles common variables and functions related
    to the metrics returned by analytics endpoints.
    """

    def __init__(self, *args):
        super().__init__(*args)  # forward all args to allow multiple inheritance
        self._start_date = None
        self._end_date = None
        self.enumerated_values = {}
        self.required_attrs = set()
        self.attrs = {}
        self._metrics = set()

    def check_enumerated_attr(self, name, value):
        """
        Check that the value of an enumerated attribute is an expected value.
        """
        values = self.enumerated_values.get(name)
        if not values:
            return
        if value not in values:
            # sort makes error testing and debugging easier
            values_list = list(values)
            try:
                values_list.sort()  # works if everything is the same type
            except TypeError:
                values_list.sort(key=str)  # works for mixed types
            raise ValueError(f"{name}: {value} is not one of {values_list}")

    def check_enumerated_attrs(self):
        """
        Check the values of all of the enumerated attributes that have been
        set with their expected values.
        """
        for attr, value in self.attrs.items():
            self.check_enumerated_attr(attr, value)

    def check_required_attrs(self):
        """
        Verify that the required attributes are set.
        """
        missing = set()
        for attr in self.required_attrs:
            if attr not in self.attrs:
                missing.add(attr)
        if missing:
            missing_list = list(missing)
            missing_list.sort()  # sort makes error testing and debugging easier
            raise AttributeError(f"missing attributes: {missing_list}")

    def start_date(self, start_date):
        """
        Required attribute. Report start date (UTC): YYYY-MM-DD.
        """
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        """
        Required attribute. Report end date (UTC): YYYY-MM-DD.
        """
        self._end_date = end_date
        return self

    def date_range(self, start_date, end_date):
        """
        Shortcut: set required start date and end date in one call.
        """
        self._start_date = start_date
        self._end_date = end_date
        return self

    def last_30_days(self):
        """
        Shortcut: set the end date to the current date and the start date
        to thirty days earlier.
        """
        today = datetime.date.today()
        today_minus_30 = today - datetime.timedelta(days=30)
        self.date_range(
            today_minus_30.strftime(self.ATTR_DATE_FORMAT),
            today.strftime(self.ATTR_DATE_FORMAT),
        )
        return self

    ATTR_DATE_FORMAT = "%Y-%m-%d"

    def check_date_attr(self, name, date):
        try:
            datetime.datetime.strptime(date, self.ATTR_DATE_FORMAT)
        except ValueError:
            raise ValueError(
                f"{name}: {date} needs to be a UTC date in YYYY-MM-DD format"
            )

    def metrics(self, metrics):
        """
        Not required, but strongly advised. May be set to 'ALL'.
        """
        self._metrics |= metrics  # union with new metrics
        return self

    def metric(self, metric):
        """
        Adds a single metric to the metric set.
        """
        self._metrics.add(metric)
        return self

    def metrics_array(self, required=True):
        """
        Returns the metrics as a sorted array.
        """
        if not self._metrics:
            # raise an exception if metrics are required but not set
            if required:
                raise AttributeError("metrics not set")
            return None

        # set order is nondeterministic, so create a sorted list
        metrics_list = list(self._metrics)
        metrics_list.sort()  # sort makes error testing and debugging easier
        return metrics_list

    def metrics_string(self, required=True):
        """
        Returns the metrics as a comma-separated string, suitable
        for a GET or POST parameter.
        """
        metrics_array = self.metrics_array(required=required)
        if not metrics_array:
            return ""
        return ",".join(metrics_array)

    def verify_attributes(self, metrics_required=False):
        # check the required start and end date attributes
        if not self._start_date:
            raise AttributeError("start date not set")
        self.check_date_attr("start_date", self._start_date)
        if not self._end_date:
            raise AttributeError("end date not set")
        self.check_date_attr("end_date", self._end_date)
        if not self._start_date <= self._end_date:
            raise ValueError("start date after end date")

        # check to make sure all of the required attributes are set
        self.check_required_attrs()

        # check all of the attributes with enumerated values
        self.check_enumerated_attrs()

    def uri_attributes(self, metrics_parameter, metrics_required):
        """
        Provides the attributes (everything after the '?') part of the URI
        for the GET or POST that requests or initiates the report.

        Note: This function does not include the leading '?' so that it
        can combined with a prefixed query if necessary.
        """
        self.verify_attributes()

        attributes = f"start_date={self._start_date}&end_date={self._end_date}"

        metrics = self.metrics_string(required=metrics_required)
        if metrics:
            attributes += f"&{metrics_parameter}={metrics}"

        # sort attributes to make order deterministic for testing
        attr_list = list(self.attrs.keys())
        attr_list.sort()  # sort makes error testing and debugging easier
        for attr in attr_list:
            attributes += f"&{attr}={self.attrs[attr]}"

        return attributes

    def data_attributes(self, metrics_parameter, metrics_required):
        """
        Provides the attributes as a dict to provide for the
        POST that requests or initiates the report.
        """
        self.verify_attributes()

        attributes = {"start_date": self._start_date, "end_date": self._end_date}

        metrics = self.metrics_array(required=metrics_required)
        if metrics:
            attributes[metrics_parameter] = metrics

        # put other attributes into the dict
        attributes.update(self.attrs)

        return attributes


class AdAnalyticsAttributes(AnalyticsAttributes):
    """
    This class extends the basic metrics to include standard
    advertising metrics.
    """

    ENUMERATED_WINDOW_DAYS = {0, 1, 7, 14, 30, 60}

    def __init__(self, *args):
        super().__init__(*args)  # forward all args to allow multiple inheritance

        # This dictionary lists values for attributes that are enumerated
        # in the API documentation. The keys are the names of the attributes,
        # and the dictionary values are sets of API-defined values.
        self.enumerated_values.update(
            {
                "granularity": {"TOTAL", "DAY", "HOUR", "WEEK", "MONTH"},
                "click_window_days": self.ENUMERATED_WINDOW_DAYS,
                "engagement_window_days": self.ENUMERATED_WINDOW_DAYS,
                "view_window_days": self.ENUMERATED_WINDOW_DAYS,
            }
        )

    def granularity(self, granularity):
        """
        TOTAL - metrics are aggregated over the specified date range.
        DAY - metrics are broken down daily.
        HOUR - metrics are broken down hourly.
        WEEK - metrics are broken down weekly.
        MONTH - metrics are broken down monthly.
        Currently, we only support hourly breakdown when data_source=REALTIME.
        """
        self.attrs["granularity"] = granularity
        return self

    def click_window_days(self, click_window_days):
        """
        Number of days to use as the conversion attribution window for a 'click' action.
        Applies to Pinterest Tag conversion metrics. Prior conversion tags use their
        defined attribution windows. If not specified, defaults to 30 days.
        """
        self.attrs["click_window_days"] = click_window_days
        return self

    def engagement_window_days(self, engagement_window_days):
        """
        Number of days to use as the conversion attribution window for an engagement
        action. Engagements include saves, pin clicks, and carousel card swipes.
        Applies to Pinterest Tag conversion metrics. Prior conversion tags use
        their defined attribution windows. If not specified, defaults to 30 days.
        """
        self.attrs["engagement_window_days"] = engagement_window_days
        return self

    def view_window_days(self, view_window_days):
        """
        Number of days to use as the conversion attribution window for
        a view action. Applies to Pinterest Tag conversion metrics. Prior
        conversion tags use their defined attribution windows. If not specified,
        defaults to 1 day.
        """
        self.attrs["view_window_days"] = view_window_days
        return self

    def conversion_report_time(self, conversion_report_time):
        """
        The date by which the conversion metrics returned from this endpoint
        will be reported. There are two dates associated with a conversion event:
        the date that the user interacted with the ad, and the date that the user
        completed a conversion event.
        """
        self.attrs["conversion_report_time"] = conversion_report_time
        return self
