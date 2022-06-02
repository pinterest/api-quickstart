import { ApiObject } from './api_object.js';

/**
 * For documentation, see the version-specific implementations of AsyncReport.
 */
export class AsyncReport extends ApiObject {
  constructor(api_config, access_token, path) {
    super(api_config, access_token);
    this.path = path;
    this.token = null;
    this.status = null;
    this._url = null;
  }

  // For documentation, see:
  // https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
  async request_report(post_data_attributes) {
    this.token = (await this.post_data(this.path, post_data_attributes)).token;
    return this.token; // so that tests can verify the token
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  async poll_report() {
    const poll_data = await this.request_data(`${this.path}?token=${this.token}`);
    this.status = poll_data.report_status;
    this._url = poll_data.url;
  }

  // Polls for the status of the report until it is complete.
  async wait_report() {
    this.reset_backoff();

    while (true) {
      await this.poll_report();
      if (this.status === 'FINISHED') {
        return;
      }

      await this.wait_backoff({
        message: `Report status: ${this.status}.`
      });
    }
  }

  // Executes the POST request to initiate the report and then the GET requests
  // to retrieve the report.
  async run(attributes) {
    await this.request_report(attributes);
    await this.wait_report();
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
