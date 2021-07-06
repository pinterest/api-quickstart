#!/usr/bin/env python
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from arguments import common_arguments

def main(argv=[]):
    """
    This script refreshes an access token originally created by using the
    the get_access_token.py script with the --write argument. The new access
    token may be printed with the --cleartext option.
    """
    parser = argparse.ArgumentParser(description='Refresh Pinterest OAuth token')
    parser.add_argument('-ct', '--cleartext', action='store_true', help='print the token in clear text')
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from user import User

    access_token = AccessToken(api_config, name=args.access_token)
    access_token.read()
    access_token.refresh()

    # Note: It is best practice not to print credentials in clear text.
    # Pinterest engineers asked for this capability to make it easier to support partners.
    if args.cleartext:
        print('Please keep clear text tokens secure!')
        print('clear text access token after refresh: ' + access_token.access_token)
    print('hashed access token after refresh: ' + access_token.hashed())

    # Use the access token to get information about the user. The purpose of this
    # call is to verify that the access token is working.
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    print('writing access token')
    access_token.write()

# If this script is being called from the command line, call the main function
# with the arguments. The other use case is to call main() from an integration test.
if __name__ == '__main__':
    main(sys.argv[1:])
