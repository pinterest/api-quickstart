import { AnalyticsAttributes, AdAnalyticsAttributes } from '../analytics_attributes.js';
import { ApiObject } from '../api_object.js';

/**
 * This module uses Pinterest API v3 and v4 in two classes:
 * - Analytics synchronously retrieves user (organic) reports.
 * - AdAnalytics synchronously retrieves advertising reports.
 */

/*
 * This class retrieves user (sometimes called "organic") metrics
 * using the v3 interface.
 *
 * The attribute functions are chainable. For example:
 *    Analytics(user_me_data['id'], api_config, access_token)
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
  // https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/v3_analytics_partner_metrics_GET
  constructor(user_id, api_config, access_token) {
    super();
    this.user_id = user_id;
    this.api_object = new ApiObject(api_config, access_token);
    Object.assign(this.enumerated_values, {
      paid: [0, 1, 2],
      in_profile: [0, 1, 2],
      from_owned_content: [0, 1, 2],
      downstream: [0, 1, 2],
      pin_format: [
        'all',
        'product',
        'standard',
        'standard_product_stl_union',
        'standard_product_union',
        'standard_stl_union',
        'stl',
        'story',
        'video'
      ],
      app_types: ['all', 'mobile', 'tablet', 'web'],
      publish_types: ['all', 'published'],
      include_curated: [0, 1, 2]
    });
  }

  // chainable attribute setters...

  paid(paid) {
    this.attrs.paid = paid;
    return this;
  }

  in_profile(in_profile) {
    this.attrs.in_profile = in_profile;
    return this;
  }

  from_owned_content(from_owned_content) {
    this.attrs.from_owned_content = from_owned_content;
    return this;
  }

  downstream(downstream) {
    this.attrs.downstream = downstream;
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

  publish_types(publish_types) {
    this.attrs.publish_types = publish_types;
    return this;
  }

  include_curated(include_curated) {
    this.attrs.include_curated = include_curated;
    return this;
  }

  // Get analytics for the user account. Specifying ad_account_id
  // works with v5 but not v3/v4.
  // https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/v3_analytics_partner_metrics_GET
  async get(ad_account_id) {
    if (ad_account_id) {
      console.log('User account analytics for shared accounts are');
      console.log('supported by Pinterest API v5, but not v3 or v4.');
      return null;
    }

    return await this.api_object.request_data(`\
/v3/partners/analytics/users/${this.user_id}/metrics/?\
${this.uri_attributes('metric_types', false)}`);
  }
}

/**
 * This class retrieves advertising delivery metrics with
 * Pinterest API version v4, which has essentially the same
 * functionality as v5. A separate module (delivery_metrics)
 * provides a way to retrieve similar metrics using the v3
 * asynchronous report functionality.
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
 * The ApiObject container implements the REST transaction used
 * to fetch the metrics.
 */
export class AdAnalytics extends AdAnalyticsAttributes {
  constructor(api_config, access_token) {
    super();
    this.api_object = new ApiObject(api_config, access_token);
    this.required_attrs.add('granularity');
    // https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_create_advertiser_delivery_metrics_report_POST
    Object.assign(this.enumerated_values, {
      attribution_types: ['INDIVIDUAL', 'HOUSEHOLD'],
      conversion_report_time: ['AD_EVENT', 'CONVERSION_EVENT']
    });
  }

  // chainable attribute setter...

  attribution_types(attribution_types) {
    this.attrs.attribution_types = attribution_types;
    return this;
  }

  async request(request_uri) {
    // Note that the uri_attributes method takes care of encoding the parameters.
    // For example, the metrics are sent in the 'columns' parameter as a
    // comma-separated string.
    return await this.api_object.request_data(
      request_uri + this.uri_attributes('columns', true));
  }

  // Get analytics for the ad account.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_advertiser_delivery_metrics_handler
  async get_ad_account(advertiser_id) {
    return await this.request(`/ads/v4/advertisers/${advertiser_id}/delivery_metrics?`);
  }

  // Get analytics for the campaign.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_campaign_delivery_metrics_handler
  async get_campaign(advertiser_id, campaign_id) {
    return await this.request(`\
/ads/v4/advertisers/${advertiser_id}/campaigns/delivery_metrics\
?campaign_ids=${campaign_id}&`);
  }

  // Get analytics for the ad group.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ad_group_delivery_metrics_handler
  async get_ad_group(advertiser_id, _campaign_id, ad_group_id) {
    return await this.request(`\
/ads/v4/advertisers/${advertiser_id}/ad_groups/delivery_metrics\
?ad_group_ids=${ad_group_id}&`);
  }

  // Get analytics for the ad.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ad_delivery_metrics_handler
  async get_ad(advertiser_id, _campaign_id, _ad_group_id, ad_id) {
    return await this.request(`\
/ads/v4/advertisers/${advertiser_id}/ads/delivery_metrics\
?ad_ids=${ad_id}&`);
  }
}
