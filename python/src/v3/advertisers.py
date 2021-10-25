from api_object import ApiObject


class Advertisers(ApiObject):
    def __init__(self, user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user_id = user_id

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_advertisers_by_owner_user_id_handler_GET
    def get(self, query_parameters=None):
        """
        Get the advertisers shared with the specified user_id.
        It's unintuitive, but the param include_acl=true is required
        to return advertisers which are shared with your account.
        """
        return self.get_iterator(
            "/ads/v3/advertisers/"
            + f"?owner_user_id={self.user_id}"
            + "&include_acl=true",
            query_parameters,
        )

    @classmethod
    def summary(cls, element, kind):
        """
        Return a string with a summary of an element returned by this module.
        """
        summary = f"{kind} ID: {element['id']} | Name: {element['name']}"
        if element.get("status"):
            summary += f" ({element['status']})"
        return summary

    @classmethod
    def print_summary(cls, element, kind):
        """
        Prints the summary of an object returned by this module.
        Similar to print_summary for other classes.
        """
        print(cls.summary(element, kind))

    @classmethod
    def print_enumeration(cls, data, kind):
        """
        Print a numbered list of elements returned by this module.
        """
        for idx, element in enumerate(data):
            summary = f"[{idx+1}] {cls.summary(element, kind)}"
            print(summary)

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_advertiser_campaigns_handler_GET
    def get_campaigns(self, ad_account_id, query_parameters=None):
        """
        Get the campaigns associated with an Ad Account.
        """
        return self.get_iterator(
            f"/ads/v3/advertisers/{ad_account_id}/campaigns/", query_parameters
        )

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_campaign_ad_groups_handler_GET
    def get_ad_groups(self, _ad_account_id, campaign_id, query_parameters=None):
        """
        Get the ad groups associated with a Campaign.
        """
        return self.get_iterator(
            f"/ads/v3/campaigns/{campaign_id}/ad_groups/", query_parameters
        )

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_ad_group_pin_promotions_handler_GET
    # Note: Ads used to be called "promoted pins" or "pin promotions."
    def get_ads(self, _ad_account_id, _campaign_id, ad_group_id, query_parameters=None):
        """
        Get the ads associated with an Ad Group.
        """
        return self.get_iterator(
            f"/ads/v3/ad_groups/{ad_group_id}/pin_promotions/", query_parameters
        )
