import { ApiObject } from '../api_object.js';

export class Advertisers extends ApiObject {
  constructor(_user_id, api_config, access_token) {
    super(api_config, access_token);
  }

  // Get the advertisers shared with the specified user_id.
  // https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/list
  async get() {
    return this.get_iterator('/v5/ad_accounts');
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
  // https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list
  async get_campaigns(ad_account_id) {
    return this.get_iterator(`/v5/ad_accounts/${ad_account_id}/campaigns`);
  }

  // Get the ad groups associated with an Ad Account and Campaign.
  // https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/list
  async get_ad_groups(ad_account_id, campaign_id) {
    return this.get_iterator(
      `/v5/ad_accounts/${ad_account_id}/ad_groups?campaign_ids=${campaign_id}`
    );
  }

  // Get the ads associated with an Ad Account, Campaign, and Ad Group.
  // https://developers.pinterest.com/docs/api/v5/#operation/ads/list
  async get_ads(ad_account_id, campaign_id, ad_group_id) {
    return this.get_iterator(`\
/v5/ad_accounts/${ad_account_id}/ads\
?campaign_ids=${campaign_id}&ad_group_ids=${ad_group_id}`);
  }
}
