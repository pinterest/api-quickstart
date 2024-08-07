from api_object import ApiObject


class User(ApiObject):
    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    # https://developers.pinterest.com/docs/api/v5/user_account-get/
    def get(self):
        return self.request_data("/v5/user_account")

    def print_summary(self, user_data):
        print("--- User Summary ---")
        print("Username:", user_data.get("username"))
        print("Account Type:", user_data.get("account_type"))
        print("Profile Image:", user_data.get("profile_image"))
        print("Website URL:", user_data.get("website_url"))
        print("--------------------")

    # https://developers.pinterest.com/docs/api/v5/boards-list/
    def get_boards(self, query_parameters=None):
        # the returned iterator handles API paging
        return self.get_iterator("/v5/boards", query_parameters)

    # https://developers.pinterest.com/docs/api/v5/pins-list/
    def get_pins(self, query_parameters=None):
        return self.get_iterator("/v5/pins", query_parameters)
