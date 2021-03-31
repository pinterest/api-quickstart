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

    # TODO: if reports are orthogonal to metrics, these methods should be in a separate class...
    def request_report(self, advertiser_id, start_date, end_date, level, metrics):
        path = (f'/ads/v3/reports/async/{advertiser_id}/delivery_metrics/' +
                f'?start_date={start_date}&end_date={end_date}' +
                '&level=' + level +
                '&metrics=' + ','.join(metrics))
        print(path)
        return self.post_data(path)['token']

    def poll_report(self, advertiser_id, report_token):
        path = (f'/ads/v3/reports/async/{advertiser_id}/delivery_metrics/' +
                f'?token={report_token}')
        return self.request_data(path)

    # TODO: probably want to use a backoff algorithm for the delay...
    def wait_report(self, advertiser_id, report_token, delay=10):
        while True:
            report_data = self.poll_report(advertiser_id, report_token)
            status = report_data['report_status']
            if status == 'FINISHED':
                return report_data['url']

            print(f'Report status: {status}. Waiting {delay} seconds...')
            time.sleep(delay)
