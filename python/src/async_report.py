from api_object import ApiObject


class AsyncReport(ApiObject):
    """
    For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports

    Subclasses must override:
       self.kind_of = String, The kind of report. Example: 'delivery_metrics'
       self.post_data_attributes() = Method that generates the data for the POST.
    """  # noqa: E501 because the long URL is okay

    def __init__(self, api_config, access_token, advertiser_id):
        super().__init__(api_config, access_token)
        self.advertiser_id = advertiser_id
        self.kind_of = None  # must be overridden by subclass
        self.token = None
        self.status = None
        self._url = None

    def post_data_attributes(self):
        raise RuntimeError("subclass must override post_data_attributes()")

    def request_report(self):
        """
        For documentation, see:
          https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler
        """
        if not self.kind_of:
            raise RuntimeError("subclass must override the kind_of report")

        # create path and set required attributes
        path = f"/ads/v4/advertisers/{self.advertiser_id}/{self.kind_of}/async"
        self.token = self.post_data(path, self.post_data_attributes())["token"]

    def poll_report(self):
        """
        For documentation, see:
          https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_async_delivery_metrics_handler

        Executes a single GET request to retrieve the status and (if available) the URL for the report.
        """  # noqa: E501 because the long URL is okay
        path = (
            f"/ads/v4/advertisers/{self.advertiser_id}/{self.kind_of}/async"
            + f"?token={self.token}"
        )
        poll_data = self.request_data(path)
        self.status = poll_data["report_status"]
        self._url = poll_data.get("url")

    def wait_report(self):
        """
        Poll for the status of the report until it is complete.
        """
        self.reset_backoff()
        while True:
            self.poll_report()
            if self.status == "FINISHED":
                return

            self.wait_backoff(f"Report status: {self.status}.")

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
        return self._url.split("/")[-1].split("?")[0]
