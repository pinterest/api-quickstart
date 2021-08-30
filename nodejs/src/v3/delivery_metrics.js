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

  // https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_delivery_metrics_handler_GET
  // Get the full list of all available delivery metrics.
  // This call is not used much in day-to-day API code, but is a useful endpoint
  // for learning about the metrics.
  async get() {
    return (await this.request_data(
      '/ads/v3/resources/delivery_metrics/')).metrics;
  }

  summary(delivery_metric) {
    return `${delivery_metric.name}: ${delivery_metric.definition}`;
  }

  // Print summary of a single metric.
  print(delivery_metric) {
    console.log(this.summary(delivery_metric));
  }

  // Print summary of data returned by get().
  print_all(delivery_metrics) {
    console.log('Available delivery metrics:');
    for (const [idx, metric] of delivery_metrics.entries()) {
      console.log(`[${idx + 1}] ${this.summary(metric)}`);
    }
  }
}

/**
 * Specifies all of the attributes for the async advertiser
 * delivery metrics report. For more information, see:
 *    https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_create_advertiser_delivery_metrics_report_POST
 *
 * The attribute functions are chainable. For example:
 * report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
 *          .start_date('2021-03-01') \
 *          .end_date('2021-03-31') \
 *          .level('PIN_PROMOTION') \
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
      'delivery_metrics', api_config, access_token, advertiser_id
    );

    // level is a required attribute
    this.required_attrs.add('level');

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

  // TODO: not sure how filters need to be encoded.
  filters(filters) {
    this.attrs.filters = filters;
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
  post_uri_attributes() {
    return this.uri_attributes('metrics', false);
  }

  // Pass attributes to AsyncReport.run().
  async run() {
    await this.async_report.run(this.post_uri_attributes());
  }

  // Pass-through methods...
  filename() {
    return this.async_report.filename();
  }

  url() {
    return this.async_report.url();
  }
}
