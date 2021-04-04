import time

from api_object import ApiObject

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

class DeliveryMetricsAsyncReport(ApiObject):
    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token)
        self.advertiser_id = advertiser_id
        self._start_date = None
        self._end_data = None
        self._level = None
        self._metrics = set()
        self.token = None
        self.status = None
        self.url = None

    def start_date(self, start_date):
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        self._end_date = end_date
        return self

    def date_range(self, date_range):
        self._start_date = date_range[0]
        self._end_date = date_range[1]
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

    def request_report(self):
        self.verify_attributes()
        # create path and set required attributes
        path = (f'/ads/v3/reports/async/{self.advertiser_id}/delivery_metrics/' +
                f'?start_date={self._start_date}&end_date={self._end_date}' +
                '&level=' + self._level +
                '&metrics=' + ','.join(self._metrics))
        print(path)
        self.token = self.post_data(path)['token']

    def poll_report(self):
        path = (f'/ads/v3/reports/async/{self.advertiser_id}/delivery_metrics/' +
                f'?token={self.token}')
        poll_data = self.request_data(path)
        self.status = poll_data['report_status']
        self.url = poll_data.get('url')

    def wait_report(self):
        delay = 1 # for backoff algorithm
        readable = 'a second' # for human-readable output of delay
        while True:
            self.poll_report()
            if self.status == 'FINISHED':
                return

            print(f'Report status: {self.status}. Waiting {readable}...')
            time.sleep(delay)
            delay = min(delay * 2, 10)
            readable = f'{delay} seconds'

    def run_report(self):
        self.request_report()
        self.wait_report()
        return self.url
