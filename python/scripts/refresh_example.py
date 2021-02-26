#!/usr/bin/env python
from os.path import dirname, abspath, join
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from access_token import AccessToken
from user import User

# get configuration from defaults and/or the environment
api_config = ApiConfig()

# Note: It's possible to use the same API configuration with
# multiple access tokens, so these objects are kept separate.
access_token = AccessToken(api_config)

# use the access token to get information about the user
user_me = User('me', api_config, access_token)
user_me_data = user_me.get()
user_me.print_summary(user_me_data)

print('trying /v3/users/me/businesses...')
user_me_businesses = user_me.get_businesses()
if user_me_businesses:
    print(user_me_businesses)

# refresh the access_token
# Note that the AccessToken encapsulates the credentials,
# so there is no need to refresh the User or other objects.
access_token.refresh()

print('accessing with refreshed access_token...')
user_me_data = user_me.get()
user_me.print_summary(user_me_data)

print('trying /v3/users/me/businesses with new_access_token...')
user_me_businesses = user_me.get_businesses()
if user_me_businesses:
    print(user_me_businesses)

# refresh the access_token again
access_token.refresh()

print('accessing with second refreshed access_token...')
user_me_data = user_me.get()
user_me.print_summary(user_me_data)
