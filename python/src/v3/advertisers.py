from api_object import ApiObject


class Advertisers(ApiObject):
    def __init__(self, user_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user_id = user_id

    # https://developers.pinterest.com/docs/redoc/#operation/ads_v3_get_advertisers_by_owner_user_id_handler_GET
    def get(self):
        """
        Get the advertisers shared with the specified user_id.
        It's unintuitive, but the param include_acl=true is required
        to return advertisers which are shared with your account.
        """
        return self.request_data(
            "/ads/v3/advertisers/"
            + f"?owner_user_id={self.user_id}"
            + "&include_acl=true"
        )

    def print_summary(self, advertisers_data):
        """
        Print summary of data returned by get().
        """
        print("Advertiser accounts available to this access token:")
        for idx, adv in enumerate(advertisers_data):
            print(f"[{idx + 1}] Name: {adv['name']}, Advertiser ID: {adv['id']}")
