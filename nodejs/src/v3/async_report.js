import { ApiObject } from '../api_object.js';

/**
 * For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
 *
 */
export class AsyncReport extends ApiObject {
  constructor(kind_of_report, api_config, access_token, advertiser_id) {
    super(api_config, access_token);
    this.advertiser_id = advertiser_id;
    this.kind_of = kind_of_report;
    this.token = null;
    this.status = null;
    this._url = null;
  }

  // For documentation, see:
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler
  async request_report(post_data_attributes) {
    // create path and set required attributes
    const path = `\
/ads/v4/advertisers/${this.advertiser_id}/${this.kind_of}/async`;

    this.token = (await this.post_data(path, post_data_attributes)).token;
    return this.token; // so that tests can verify the token
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  // For documentation, see:
  //   https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_async_delivery_metrics_handler
  async poll_report() {
    const path = `\
/ads/v4/advertisers/${this.advertiser_id}/${this.kind_of}/async\
?token=${this.token}`;

    const poll_data = await this.request_data(path);
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
