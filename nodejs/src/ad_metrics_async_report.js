import { AdMetricsAsyncReportCommon } from '../ad_metrics_async_report_common.js';
import { AsyncReport } from '../async_report.js';

/**
 * For documentation, see: https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report
 *
 * AdMetricsAsyncReport is a subclass of the API-version-independent
 * AdMetricsAsyncReportCommon class and contains the API-version-specific
 * AsynchReport.
 *
 * The AsyncReport container is used to perform the process of requesting
 * and waiting for the asynchronous report to be ready.
 */
export class AdMetricsAsyncReport extends AdMetricsAsyncReportCommon {
  constructor(api_config, access_token, advertiser_id) {
    super();
    this.async_report = new AsyncReport(
      api_config, access_token, `/v5/ad_accounts/${advertiser_id}/reports`
    );
  }
}
