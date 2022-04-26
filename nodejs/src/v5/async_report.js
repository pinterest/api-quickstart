import { AsyncReportCommon } from '../async_report_common.js';

/**
 * For documentation, see: https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report
 *
 */
export class AsyncReport extends AsyncReportCommon {
  constructor(api_config, access_token, advertiser_id) {
    super(api_config, access_token);
    this.advertiser_id = advertiser_id;
  }

  // For documentation, see:
  // https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
  async request_report(post_data_attributes) {
    // create path and set required attributes
    const path = `/v5/ad_accounts/${this.advertiser_id}/reports`;

    return await super.request_report(path, post_data_attributes);
  }

  // Executes a single GET request to retrieve the status and (if available)
  // the URL for the report.
  // For documentation, see:
  //   https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
  async poll_report() {
    const path = `\
/v5/ad_accounts/${this.advertiser_id}/reports\
?token=${this.token}`;

    await super.poll_report(path);
  }

  // Polls for the status of the report until it is complete.
  async wait_report() {
    const path = `\
/v5/ad_accounts/${this.advertiser_id}/reports\
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
