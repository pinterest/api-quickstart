import { ApiObject } from '../api_object.js';

export class Advertisers extends ApiObject {
  constructor(user_id, api_config, access_token) {
    super(api_config, access_token);
    this.user_id = user_id;
  }

  // Get the advertisers shared with the specified user_id.
  // It's unintuitive, but the param include_acl=true is required
  // to return advertisers which are shared with your account.
  // https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_advertisers_by_owner_user_id_handler_GET
  async get() {
    return this.get_iterator(
      `/ads/v3/advertisers/?owner_user_id=${this.user_id}&include_acl=true`);
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
  // https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_advertiser_campaigns_handler_GET
  async get_campaigns(ad_account_id) {
    return this.get_iterator(`/ads/v3/advertisers/${ad_account_id}/campaigns/`);
  }

  // Get the ad groups associated with an Ad Account and Campaign.
  // https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_campaign_ad_groups_handler_GET
  async get_ad_groups(_ad_account_id, campaign_id) {
    return this.get_iterator(`/ads/v3/campaigns/${campaign_id}/ad_groups/`);
  }

  // Get the ads associated with an Ad Account, Campaign, and Ad Group.
  // https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_ad_group_pin_promotions_handler_GET
  async get_ads(_ad_account_id, _campaign_id, ad_group_id) {
    return this.get_iterator(`/ads/v3/ad_groups/${ad_group_id}/pin_promotions/`);
  }
}
