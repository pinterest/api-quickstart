from api_object import ApiObject


class AsyncReport(ApiObject):
    """
    For documentation, see the version-specific implementations of AsyncReport.
    """

    def __init__(self, api_config, access_token, path):
        super().__init__(api_config, access_token)
        self.path = path
        self.token = None
        self.status = None
        self._url = None

    def post_data_attributes(self):
        raise RuntimeError("subclass must override post_data_attributes()")

    def request_report(self):
        """
        For documentation, see:
          https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
        """
        self.token = self.post_data(self.path, self.post_data_attributes())["token"]
        return self.token
        # so that tests can verify the token

    def poll_report(self):
        """
        Executes a single GET request to retrieve the status and
        (if available) the URL for the report.
        """
        poll_data = self.request_data(f"{self.path}?token={self.token}")
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
