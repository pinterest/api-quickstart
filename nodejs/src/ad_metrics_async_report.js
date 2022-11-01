import { AdAnalyticsAttributes } from './analytics_attributes.js';
import { AsyncReport } from './async_report.js';

/**
 * Specifies all of the attributes for the async advertiser
 * metrics report. For more information, see:
 *  https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report
 *
 *
 * The attribute functions are chainable. For example:
 * report = AdMetricsAsyncReport(api_config, access_token, advertiser_id) \
 *          .start_date('2021-03-01') \
 *          .end_date('2021-03-31') \
 *          .level('PIN_PROMOTION') \
 *          .granularity('DAY') \
 *          .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'}) \
 *          .report_format('csv')
 *
 * The parent class AdAnalyticsAttributes implements the parameters that
 * are shared between synchronous and asynchronous reports.
 *
 * The AsyncReport container is used to perform the process of requesting
 * and waiting for the asynchronous report to be ready.
 */
export class AdMetricsAsyncReport extends AdAnalyticsAttributes {
  constructor(api_config, access_token, advertiser_id) {
    super();
    this.async_report = new AsyncReport(
      api_config, access_token, `/v5/ad_accounts/${advertiser_id}/reports`
    );

    // set required attributes
    this.required_attrs.add('level');
    this.required_attrs.add('granularity');

    // This dictionary lists values for attributes that are enumerated
    // in the API documentation. The keys are the names of the attributes,
    // and the dictionary values are sets of API-defined values.
    Object.assign(this.enumerated_values, {
      entity_fields: [
        'AD_GROUP_ID',
        'AD_GROUP_NAME',
        'AD_GROUP_STATUS',
        'CAMPAIGN_ID',
        'CAMPAIGN_MANAGED_STATUS',
        'CAMPAIGN_NAME',
        'CAMPAIGN_STATUS',
        'PIN_PROMOTION_ID',
        'PIN_PROMOTION_NAME',
        'PIN_PROMOTION_STATUS',
        'PRODUCT_GROUP_ID'
      ],
      level: [
        'ADVERTISER',
        'AD_GROUP',
        'CAMPAIGN',
        'ITEM',
        'KEYWORD',
        'PIN_PROMOTION',
        'PIN_PROMOTION_TARGETING',
        'PRODUCT_GROUP',
        'PRODUCT_GROUP_TARGETING',
        'PRODUCT_ITEM',
        'SEARCH_QUERY'
      ],
      report_format: ['CSV', 'JSON'],
      tag_version: [2, 3, '2', '3']
    });
  }

  // Required attribute. Requested report type.
  level(level) {
    this.attrs.level = level;
    return this;
  }

  // Additional fields that you would like included for each entity in the
  // Ads Metrics Report. Fields will be prefixed with the requested level
  // when returned in the report, for example if CAMPAIGN_ID is requested at the
  // AD_GROUP level, this field will be called AD_GROUP_CAMPAIGN_ID.
  // Please note that entity fields can only be requested for the specified level
  // and its parents, for example, for an AD_GROUP level request CAMPAIGN and
  // AD_GROUP entity_fields can be requested, but PIN_PROMOTION entity_fields
  // cannot.
  entity_fields(entity_fields) {
    this.attrs.entity_fields = entity_fields;
    return this;
  }

  // Filters must be a list of structures with fields as specified by the API.
  filters(filters) {
    this.attrs.metrics_filters = filters;
    return this;
  }

  // Specification for formatting report data.
  report_format(report_format) {
    this.attrs.report_format = report_format;
    return this;
  }

  // By default, Pinterest Tag metrics are returned. To view metrics
  // from prior conversion tags, set this field to 2.
  tag_version(tag_version) {
    this.attrs.tag_version = tag_version;
    return this;
  }

  // expose attributes for testing
  post_data_attributes() {
    // metrics are required
    return this.data_attributes('columns', true);
  }

  // Pass attributes to AsyncReport.run().
  async run() {
    await this.async_report.run(this.post_data_attributes());
  }

  // Pass-through methods...
  filename() {
    return this.async_report.filename();
  }

  url() {
    return this.async_report.url();
  }
}
