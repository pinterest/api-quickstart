import { ApiObject } from '../api_object.js';

export class Advertisers extends ApiObject {
  constructor(user_id, api_config, access_token) {
    super(api_config, access_token);
    this.user_id = user_id;
  }

  // Get the advertisers shared with the specified user_id.
  // It's unintuitive, but the param include_acl=true is required
  // to return advertisers which are shared with your account.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_advertisers_handler
  async get(query_parameters) {
    // query_parameters are available for consistency with other endpoints.
    // There are no other query_parameters available for this endpoint.
    return this.get_iterator(
      `/ads/v4/advertisers/?owner_user_id=${this.user_id}&include_acl=true`,
      query_parameters);
  }

  // Return a string with a summary of an element returned by this module.
  summary(element, kind) {
    let summary = `${kind} ID: ${element.id} | Name: ${element.name}`;
    if (element.status) {
      summary += ` (${element.status})`;
    }
    return summary;
  }

  // Prints the summary of an object returned by this module.
  // Similar to print_summary for other classes.
  print_summary(element, kind) {
    console.log(this.summary(element, kind));
  }

  // Print a numbered list of elements returned by this module.
  print_enumeration(data, kind) {
    for (const [idx, element] of data.entries()) {
      console.log(`[${idx + 1}] ${this.summary(element, kind)}`);
    }
  }

  // Get the campaigns associated with an Ad Account.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_campaigns_handler
  async get_campaigns(ad_account_id, query_parameters) {
    return this.get_iterator(`/ads/v4/advertisers/${ad_account_id}/campaigns`,
      query_parameters);
  }

  // Get the ad groups associated with an Ad Account and Campaign.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ad_groups_handler
  async get_ad_groups(ad_account_id, campaign_id, query_parameters) {
    return this.get_iterator(
      `/ads/v4/advertisers/${ad_account_id}/ad_groups?campaign_ids=${campaign_id}`,
      query_parameters
    );
  }

  // Get the ads associated with an Ad Account, Campaign, and Ad Group.
  // https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_ads_handler
  async get_ads(ad_account_id, campaign_id, ad_group_id, query_parameters) {
    return this.get_iterator(`\
/ads/v4/advertisers/${ad_account_id}/ads\
?campaign_ids=${campaign_id}&ad_group_ids=${ad_group_id}`,
    query_parameters);
  }
}
