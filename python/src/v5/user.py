from api_object import ApiObject
from v5.board import Board

class UserPinIterator:
    """
    This class emulates the ability to list all pins for a user.
    """
    def __init__(self, boards, api_config, access_token):
        self.api_config = api_config
        self.access_token = access_token
        self.board_iterator = boards
        self.pin_iterator = iter([])

    def __iter__(self):
        return self

    def __next__(self):
        # fetch a pin
        for pin in self.pin_iterator:
            return pin
        # no more pins, try next board
        for board_data in self.board_iterator:
            board = Board(board_data['id'], self.api_config, self.access_token)
            self.pin_iterator = board.get_pins()
            return self.__next__() # recursively try pin iterator

        raise StopIteration # no more boards

class User(ApiObject):
    def __init__(self, user, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user = user

    # https://developers.pinterest.com/docs/v5/#tag/user_accounts
    def get(self):
        return self.request_data('/v5/user_account')

    def get_businesses(self):
        print('Businesses endpoint is not available in v5.')
        return None

    def print_summary(self, user_data):
        print('--- User Summary ---')
        print('Username:', user_data.get('username'))
        print('Account Type:', user_data.get('account_type'))
        print('Profile Image:',user_data.get('profile_image'))
        print('Website URL:', user_data.get('website_url'))
        print('--------------------')

    # https://developers.pinterest.com/docs/v5/#operation/boards/list
    def get_boards(self, user_data, query_parameters={}):
        path = '/v5/boards'
        if query_parameters:
            delimiter = '?'
            for query_parameter, value in query_parameters.items():
                path += delimiter + query_parameter + '=' + str(value)
                delimiter = '&'
        return self.get_iterator(path) # the returned iterator handles API paging

    # getting all of a user's pins is not supported, so iterate through boards
    def get_pins(self, user_data, query_parameters={}):
        return UserPinIterator(self.get_boards(user_data, query_parameters),
                               self.api_config, self.access_token)
