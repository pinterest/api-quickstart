import time

from api_object import ApiObject

class AsyncReport(ApiObject):
    """
    For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports

    Subclasses must override:
       self.kind_of = String, The kind of report. Example: 'delivery_metrics'
       self.post_uri_attributes() = Method that generates the attributes for the POST.
    """
    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token)
        self.advertiser_id = advertiser_id
        self.kind_of = None # must be overridden by subclass
        self.token = None
        self.status = None
        self._url = None

    def post_uri_attributes(self):
        raise RuntimeError('subclass must override post_uri_attributes()')

    def request_report(self):
        if not self.kind_of:
            raise RuntimeError('subclass must override the kind_of report')

        # create path and set required attributes
        path = (f'/ads/v3/reports/async/{self.advertiser_id}/{self.kind_of}/' +
                self.post_uri_attributes())
        self.token = self.post_data(path)['token']

    def poll_report(self):
        """
        For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_get_advertiser_delivery_metrics_report_handler_GET

        Executes a single GET request to retrieve the status and (if available) the URL for the report.
        """
        path = (f'/ads/v3/reports/async/{self.advertiser_id}/{self.kind_of}/' +
                f'?token={self.token}')
        poll_data = self.request_data(path)
        self.status = poll_data['report_status']
        self._url = poll_data.get('url')

    def wait_report(self):
        """
        Polls for the status of the report until it is complete. Uses an exponential backoff
        algorithm (up to a 10 second maximum delay) to determine the appropriate amount of time
        to wait.
        """
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

    def run(self):
        """
        Executes the POST request to initiate the report and then the GET requests
        to retrieve the report.
        """
        self.request_report()
        self.wait_report()

    def url(self):
        return self._url

    def filename(self):
        """
        Find the file name in the report URL by taking the characters
        after the last slash but before the question mark. A typical URL
        has a format that looks like this:
        https://pinterest-cityname.s3.region.amazonaws.com/async_reporting_v3/x-y-z/metrics_report.txt?very-long-credentials-string
        """
        return self._url.split('/')[-1].split('?')[0]
