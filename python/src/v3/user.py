from v3.api_object import ApiObject # specifying v3 required for unit tests

class User(ApiObject):
    def __init__(self, user, api_config, access_token):
        super().__init__(api_config, access_token)
        self.user = user

    def get(self):
        return self.request_data('/v3/users/{}/'.format(self.user))

    def get_businesses(self):
        return self.request_data('/v3/users/{}/businesses/'.format(self.user))

    def print_summary(self, user_data):
        print('--- User Summary ---')
        print('ID: ' + user_data['id'])
        print('Full Name: ' + user_data['full_name'])
        print('About: ' + user_data['about'])
        print('Profile URL: ' + str(user_data.get('profile_url')))
        print('Pin Count: ' + str(user_data['pin_count']))
        print('--------------------')

    # documentation: https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET
    def get_boards(self, user_data, query_parameters={}):
        path = f"/v3/users/{user_data['id']}/boards/feed/"
        if query_parameters:
            delimiter = '?'
            for query_parameter, value in query_parameters.items():
                path += delimiter + query_parameter + '=' + str(value)
                delimiter = '&'
        return self.get_iterator(path) # the returned iterator handles API paging

    def get_pins(self, user_data, query_parameters={}):
        path = f"/v3/users/{user_data['id']}/pins/"
        if query_parameters:
            delimiter = '?'
            for query_parameter, value in query_parameters.items():
                path += delimiter + query_parameter + '=' + str(value)
                delimiter = '&'
        # TODO: generic iterator using bookmark in ApiObject
        return self.get_iterator(path) # the returned iterator handles API paging
