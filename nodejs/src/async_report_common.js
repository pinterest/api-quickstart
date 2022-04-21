import { ApiObject } from './api_object.js';

/**
 * For documentation, see the version-specific implementations of AsyncReport.
 */
export class AsyncReportCommon extends ApiObject {
  constructor(api_config, access_token) {
    super(api_config, access_token);
    this.token = null;
    this.status = null;
    this._url = null;
  }

  async request_report(path, post_data_attributes) {
    this.token = (await this.post_data(path, post_data_attributes)).token;
    return this.token; // so that tests can verify the token
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  async poll_report(path) {
    const poll_data = await this.request_data(path);
    this.status = poll_data.report_status;
    this._url = poll_data.url;
  }

  // Polls for the status of the report until it is complete.
  async wait_report(path) {
    this.reset_backoff();

    while (true) {
      await this.poll_report(path);
      if (this.status === 'FINISHED') {
        return;
      }

      await this.wait_backoff({
        message: `Report status: ${this.status}.`
      });
    }
  }

  url() {
    return this._url;
  }

  // Find the file name in the report URL by taking the characters
  // after the last slash but before the question mark. A typical URL
  // has a format that looks like this:
  //   https://pinterest-cityname.s3.region.amazonaws.com/async_reporting_v3/x-y-z/metrics_report.txt?very-long-credentials-string
  filename() {
    return this._url.split('/').pop().split('?')[0];
  }
}
