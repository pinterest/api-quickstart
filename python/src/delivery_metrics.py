import datetime

from api_object import ApiObject
from async_report import AsyncReport

class DeliveryMetrics(ApiObject):
    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    def get(self):
        """
        Get the available metrics.
        """
        return self.request_data('/ads/v3/resources/delivery_metrics/').get('metrics')

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
        print('Available delivery metrics:')
        for idx, metric in enumerate(delivery_metrics):
            print(f"[{idx + 1}] " + self.summary(metric))

class DeliveryMetricsAsyncReport(AsyncReport):
    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token, advertiser_id)
        self.kind_of = 'delivery_metrics' # override required by superclass
        self._start_date = None
        self._end_data = None
        self._level = None
        self._metrics = set()

    def start_date(self, start_date):
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        self._end_date = end_date
        return self

    def date_range(self, start_date, end_date):
        self._start_date = start_date
        self._end_date = end_date
        return self

    def last_30_days(self):
        today = datetime.date.today()
        today_minus_30 = today - datetime.timedelta(days=30)
        self.date_range(today_minus_30, today)
        return self

    def level(self, level):
        self._level = level
        return self

    def metrics(self, metrics):
        self._metrics |= metrics # union with new metrics
        return self

    def metric(self, metric):
        self._metrics.add(metric)
        return self

    def verify_attributes(self):
        if not self._start_date:
            raise AttributeError('start date not set')
        if not self._end_date:
            raise AttributeError('end date not set')
        if not self._start_date <= self._end_date:
            raise ValueError('start date after end date')
        if not self._level:
            raise AttributeError('level not set')
        if not self._metrics:
            raise AttributeError('metrics not set')

    def post_uri_attributes(self):
        """
        This override is required by the superclass AsyncReport.

        Provides the attributes (everything after the '?') part of the URI
        for the POST that initiates the report.
        """
        self.verify_attributes()
        return (f'?start_date={self._start_date}&end_date={self._end_date}' +
                '&level=' + self._level +
                '&metrics=' + ','.join(self._metrics))
