#!/usr/bin/env python
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from access_token import AccessToken
from oauth_scope import Scope
from user import User

def main(argv=[]):
    parser = argparse.ArgumentParser(description='Get Pinterest OAuth token')
    parser.add_argument('-w', '--write', action='store_true', help='write access token to file')
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config)
    access_token.fetch(scopes=[Scope.READ_USERS])

    print('hashed access token: ' + access_token.hashed())
    try:
        print('hashed refresh token: ' + access_token.hashed_refresh_token())
    except:
        print('no refresh token')

    # save the token, if requested
    if args.write:
        print('writing access token')
        access_token.write()

    # use the access token to get information about the user
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

if __name__ == '__main__':
    main(sys.argv[1:])
