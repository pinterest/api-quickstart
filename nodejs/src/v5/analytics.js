import { AnalyticsAttributes, AdAnalyticsAttributes } from '../analytics_attributes.js';
import { ApiObject } from '../api_object.js';

/**
 * This module uses Pinterest API v5 in two classes:
 * - Analytics synchronously retrieves user (organic) reports.
 * - AdAnalytics synchronously retrieves advertising reports.
 */

/*
 * This class retrieves user (sometimes called "organic") metrics
 * using the v5 interface.
 *
 * The attribute functions are chainable. For example:
 *    Analytics(null, api_config, access_token)
 *    .last_30_days()
 *    .metrics(['IMPRESSION', 'PIN_CLICK_RATE'])
 *
 * The AnalyticsAttributes parent class implements parameters that
 * are common to all analytics reports.
 *
 * The ApiObject container implements the REST transaction used
 * to fetch the metrics.
 */
export class Analytics extends AnalyticsAttributes {
  // https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics
  constructor(_user_id, api_config, access_token) {
    super();
    this.api_object = new ApiObject(api_config, access_token);
    Object.assign(this.enumerated_values, {
      from_claimed_content: ['Other', 'Claimed', 'Both'],
      pin_format: ['all', 'product', 'regular', 'video'],
      app_types: ['all', 'mobile', 'tablet', 'web'],
      split_field: [
        'NO_SPLIT',
        'APP_TYPE',
        'CONTENT_TYPE',
        'OWNED_CONTENT',
        'SOURCE',
        'PIN_FORMAT_CONVERSION_TYPE',
        'ATTRIBUTION_EVENT'
      ]
    });
  }

  // chainable attribute setters...

  from_claimed_content(from_claimed_content) {
    this.attrs.from_claimed_content = from_claimed_content;
    return this;
  }

  pin_format(pin_format) {
    this.attrs.pin_format = pin_format;
    return this;
  }

  app_types(app_types) {
    this.attrs.app_types = app_types;
    return this;
  }

  split_field(split_field) {
    // The split_field attribute is not yet implemented in the Pinterest API.
    // To work around this issue, use the appropriate filter attribute
    // and send multiple requests. For example, instead of setting
    // split_field to app_type, send three requests -- each with one of
    // the possible app_types: mobile, tablet, and web.
    throw new Error('split_field attribute not yet implemented in the Pinterest API');

    // When the split_field attribute is implemented in the Pinterest API,
    // remove the above comment and Error and uncomment the next two lines
    // of code.

    // this.attrs.split_field = split_field;
    // return this;
  }

  // Get analytics for the user account. If ad_account_id is set, get user
  // analytics associated with the specified Ad Account.
  // https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics
  async get(ad_account_id) {
    if (ad_account_id) {
      this.attrs.ad_account_id = ad_account_id;
    }

    try {
      return await this.api_object.request_data(`\
/v5/user_account/analytics?\
${this.uri_attributes('metric_types', false)}`);
    } finally {
      delete this.attrs.ad_account_id;
    }
  }
}

/**
 * This class retrieves advertising delivery metrics with
 * Pinterest API version v5.
 *
 * The attribute functions are chainable. For example:
 *    AdAnalytics(api_config, access_token).attributes
 *    .last_30_days()
 *    .metrics({'SPEND_IN_DOLLAR', 'TOTAL_CLICKTHROUGH'})
 *    .granularity('DAY')
 *
 * The AdAnalyticsAttributes parent class implements parameters that
 * are common to all advertising reports.
 *
 * Note that in v5, the metrics are provided to the API using the
 * 'columns' parameter, which is encoded as a comma-separated string.
 *
 * The ApiObject container implements the REST transaction used
 * to fetch the metrics.
 */
export class AdAnalytics extends AdAnalyticsAttributes {
  constructor(api_config, access_token) {
    super();
    this.api_object = new ApiObject(api_config, access_token);
    this.required_attrs.add('granularity');
    Object.assign(this.enumerated_values, {
      // https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
      conversion_report_time: ['TIME_OF_AD_ACTION', 'TIME_OF_CONVERSION']
    });
  }

  async request(request_uri) {
    // Note that the uri_attributes method takes care of encoding the parameters.
    // For example, the metrics are sent in the 'columns' parameter as a
    // comma-separated string.
    return await this.api_object.request_data(
      request_uri + this.uri_attributes('columns', true));
  }

  // Get analytics for the ad account.
  // https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
  async get_ad_account(ad_account_id) {
    return await this.request(`/v5/ad_accounts/${ad_account_id}/analytics?`);
  }

  // Get analytics for the campaign.
  // https://developers.pinterest.com/docs/api/v5/#operation/campaigns/analytics
  async get_campaign(ad_account_id, campaign_id) {
    return await this.request(`\
/v5/ad_accounts/${ad_account_id}/campaigns/analytics\
?campaign_ids=${campaign_id}&`);
  }

  // Get analytics for the ad group.
  // https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics
  async get_ad_group(ad_account_id, _campaign_id, ad_group_id) {
    return await this.request(`\
/v5/ad_accounts/${ad_account_id}/ad_groups/analytics\
?ad_group_ids=${ad_group_id}&`);
  }

  // Get analytics for the ad.
  // https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics
  async get_ad(ad_account_id, _campaign_id, _ad_group_id, ad_id) {
    return await this.request(`\
/v5/ad_accounts/${ad_account_id}/ads/analytics\
?ad_ids=${ad_id}&`);
  }
}
