from api_object import ApiObject


class Analytics(ApiObject):
    def __init__(self, _user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        # TODO: parameterize
        self.start_date = '2021-07-01'
        self.end_date = '2021-08-12'
        self.columns = ['SPEND_IN_DOLLAR', 'TOTAL_CLICKTHROUGH']
        self.granularity = 'DAY'

    def date_query(self):
        return f"start_date={self.start_date}&end_date={self.end_date}"

    def granularity_query(self):
        return f"&granularity={self.granularity}"

    def columns_query(self):
        return f"&columns={'%2C'.join(self.columns)}"

    def request(self, request_uri, has_ad_account):
        if '?' in request_uri:
            request_uri += "&"
        else:
            request_uri += "?"
        request_uri += self.date_query()
        if has_ad_account:
            request_uri += self.columns_query()
            request_uri += self.granularity_query()
        return self.request_data(request_uri)

    # https://developers.pinterest.com/docs/v5/#operation/account/analytics
    def get(self, ad_account_id=None):
        """
        Get analytics for the user account.
        """
        request_uri = "/v5/user_account/analytics"
        if ad_account_id:
            request_uri += f"?ad_account_id={ad_account_id}"
        return self.request(request_uri, False)

    # https://developers.pinterest.com/docs/v5/#operation/advertisers/analytics
    def get_ad_account(self, ad_account_id):
        """
        Get analytics for the ad account.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/analytics"
        return self.request(request_uri, True)

    # https://developers.pinterest.com/docs/v5/#operation/campaigns/analytics
    def get_campaign(self, ad_account_id, campaign_id):
        """
        Get analytics for the campaign.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/campaigns/analytics"
        request_uri += f"?campaign_ids={campaign_id}"
        return self.request(request_uri, True)

    # https://developers.pinterest.com/docs/v5/#operation/ad_groups/analytics
    def get_ad_group(self, ad_account_id, _campaign_id, ad_group_id):
        """
        Get analytics for the ad group.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ad_groups/analytics"
        request_uri += f"?ad_group_ids={ad_group_id}"
        return self.request(request_uri, True)

    # https://developers.pinterest.com/docs/v5/#operation/ads/analytics
    def get_ad(self, ad_account_id, _campaign_id, _ad_group_id, ad_id):
        """
        Get analytics for the ad.
        """
        request_uri = f"/v5/ad_accounts/{ad_account_id}/ads/analytics"
        request_uri += f"?ad_ids={ad_id}"
        return self.request(request_uri, True)
