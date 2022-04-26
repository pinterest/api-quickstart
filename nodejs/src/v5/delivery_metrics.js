import { AdAnalyticsAttributes } from '../analytics_attributes.js';
import { ApiObject } from '../api_object.js';
import { AsyncReport } from './async_report.js';

/**
 * This module has two classes:
 * - DeliveryMetrics retrieves the complete list of metrics
 *   available for advertising delivery analytics.
 * - DeliveryMetricsAsyncReport sets up and retrieves a
 *   metrics report asynchronously.
 */

// Use this class to get and to print all of the available
// advertising delivery metrics.
export class DeliveryMetrics extends ApiObject {
  // No constructor is required, because the parent constructor
  // should be called automagically. See:
  //   https://eslint.org/docs/rules/no-useless-constructor

  // The full list of all available delivery metrics is available in v3 but not v5.
  async get() {
    throw new Error('Metric definitions are not available in API version v5.');
  }
}

/**
 * Specifies all of the attributes for the async advertiser
 * delivery metrics report. For more information, see:
 *    https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler
 *
 * The attribute functions are chainable. For example:
 * report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
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
export class DeliveryMetricsAsyncReport extends AdAnalyticsAttributes {
  constructor(api_config, access_token, advertiser_id) {
    super();
    this.async_report = new AsyncReport(
      api_config, access_token, advertiser_id
    );

    // set required attributes
    this.required_attrs.add('level');
    this.required_attrs.add('granularity');

    // This dictionary lists values for attributes that are enumerated
    // in the API documentation. The keys are the names of the attributes,
    // and the dictionary values are sets of API-defined values.
    Object.assign(this.enumerated_values, {
      data_source: ['OFFLINE', 'REALTIME'],
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
      report_format: ['csv', 'json'],
      tag_version: [2, 3, '2', '3']
    });
  }

  // Required attribute. Requested report type.
  level(level) {
    this.attrs.level = level;
    return this;
  }

  // Either OFFLINE or REALTIME. Offline metrics have a long retention and are
  // used for billing (source of truth). Realtime metrics have latest metrics
  // (including today) but only have a 72-hour retention. In addition, realtime
  // metrics are expected to be an estimation and could be slightly inaccurate.
  // Please note that only a limited set of metrics are available for realtime data.
  data_source(data_source) {
    this.attrs.data_source = data_source;
    return this;
  }

  // Additional fields that you would like included for each entity in the
  // Delivery Metrics Report. Fields will be prefixed with the requested level
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
    this.attrs.filters = JSON.stringify(filters);
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
