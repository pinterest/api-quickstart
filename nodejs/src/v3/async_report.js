import { ApiObject } from '../api_object.js';

/**
 * For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
 *
 * Subclasses must override:
 *    this.kind_of = String, The kind of report. Example: 'delivery_metrics'
 *    this.post_uri_attributes() = Method that generates the attributes for the POST.
 */
export class AsyncReport extends ApiObject {
  constructor(api_config, access_token, advertiser_id) {
    super(api_config, access_token);
    this.advertiser_id = advertiser_id;
    this.kind_of = null; // must be overridden by subclass
    this.token = null;
    this.status = null;
    this._url = null;
  }

  post_uri_attributes() {
    throw new Error('subclass must override post_uri_attributes()');
  }

  // For documentation, see:
  // https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_create_advertiser_delivery_metrics_report_POST
  async request_report() {
    if (!this.kind_of) {
      throw  Error('subclass must override the kind_of report');
    }

    // create path and set required attributes
    const path = `\
/ads/v3/reports/async/${this.advertiser_id}/${this.kind_of}/\
${this.post_uri_attributes()}`;

    this.token = (await this.post_data(path))['token'];
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  // For documentation, see:
  //   https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_get_advertiser_delivery_metrics_report_handler_GET
  async poll_report() {
    const path = `\
/ads/v3/reports/async/${this.advertiser_id}/${this.kind_of}/\
?token=${this.token}`;

    const poll_data = await this.request_data(path);
    this.status = poll_data['report_status'];
    this._url = poll_data.['url'];
  }

  // Polls for the status of the report until it is complete. Uses an
  // exponential backoff algorithm (up to a 10 second maximum delay) to
  // determine the appropriate amount of time to wait.
  async wait_report() {
    var delay = 1; // for backoff algorithm
    var readable = 'a second'; // for human-readable output of delay

    while (true) {
      await this.poll_report();
      if (this.status === 'FINISHED') {
        return;
      }

      console.log(`Report status: ${this.status}. Waiting ${readable}...`);
      await new Promise(resolve => setTimeout(resolve, delay * 1000));
      delay = Math.min(delay * 2, 10)
      readable = `${delay} seconds`;
    }
  }

  // Executes the POST request to initiate the report and then the GET requests
  // to retrieve the report.
  async run() {
    await this.request_report();
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