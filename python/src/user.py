from api_object import ApiObject

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
        print('Full Name: ' + user_data['full_name'])
        print('About: ' + user_data['about'])
        print('Profile URL: ' + str(user_data.get('profile_url')))
        print('Pin Count: ' + str(user_data['pin_count']))
        print('--------------------')
