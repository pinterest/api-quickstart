from openapi_client.apis.tags import boards_api, user_account_api

from api_object import ApiObject
from board import Board


class UserPinIterator:
    """
    This class emulates the ability to list all pins for a user.
    """

    def __init__(self, boards, api_config, access_token, query_parameters):
        self.api_config = api_config
        self.access_token = access_token
        self.board_iterator = boards
        self.pin_iterator = iter([])
        self.query_parameters = query_parameters

    def __iter__(self):
        return self

    def __next__(self):
        # fetch a pin
        for pin in self.pin_iterator:
            return pin
        # no more pins, try next board
        for board_data in self.board_iterator:
            board = Board(board_data["id"], self.api_config, self.access_token)
            self.pin_iterator = board.get_pins(self.query_parameters)
            return self.__next__()  # recursively try pin iterator

        raise StopIteration  # no more boards


class User(ApiObject):
    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user_api = user_account_api.UserAccountApi(api_config.api_client)
        self.boards_api = boards_api.BoardsApi(api_config.api_client)
        # TODO: The openapi client conflates api and access token configuration.
        # Need to understand how to change the quickstart to support
        # multiple access tokens, probably by creating multiple api_configs.
        api_config.configuration.access_token = access_token.access_token

    # https://developers.pinterest.com/docs/api/v5/#tag/user_account
    def get(self):
        # Example of call to openapi client.
        # TODO: Need to understand logging better.
        return self.user_api.user_account_get().body

    def print_summary(self, user_data):
        print("--- User Summary ---")
        print("Username:", user_data.get("username"))
        print("Account Type:", user_data.get("account_type"))
        print("Profile Image:", user_data.get("profile_image"))
        print("Website URL:", user_data.get("website_url"))
        print("--------------------")

    # https://developers.pinterest.com/docs/api/v5/#operation/boards/list
    def get_boards(self, user_data, query_parameters=None):
        # the returned iterator handles API paging
        return self.get_openapi_iterator(self.boards_api.boards_list, query_parameters)

    # getting all of a user's pins is not supported, so iterate through boards
    def get_pins(self, user_data, query_parameters=None):
        return UserPinIterator(
            self.get_boards(user_data, query_parameters),
            self.api_config,
            self.access_token,
            query_parameters,
        )
