import { AsyncReportCommon } from '../async_report_common.js';

/**
 * For documentation, see: https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
 *
 */
export class AsyncReport extends AsyncReportCommon {
  constructor(kind_of_report, api_config, access_token, advertiser_id) {
    super(api_config, access_token);
    this.advertiser_id = advertiser_id;
    this.kind_of = kind_of_report;
  }

  // For documentation, see:
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler
  async request_report(post_data_attributes) {
    // create path and set required attributes
    const path = `\
/ads/v4/advertisers/${this.advertiser_id}/${this.kind_of}/async`;

    return await super.request_report(path, post_data_attributes);
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  // For documentation, see:
  //   https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_async_delivery_metrics_handler
  async poll_report() {
    const path = `\
/ads/v4/advertisers/${this.advertiser_id}/${this.kind_of}/async\
?token=${this.token}`;

    await super.poll_report(path);
  }

  // Polls for the status of the report until it is complete.
  async wait_report() {
    const path = `\
/ads/v4/advertisers/${this.advertiser_id}/${this.kind_of}/async\
?token=${this.token}`;

    await super.wait_report(path);
  }

  // Executes the POST request to initiate the report and then the GET requests
  // to retrieve the report.
  async run(attributes) {
    await this.request_report(attributes);
    await this.wait_report();
  }
}
