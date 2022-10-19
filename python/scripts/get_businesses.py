#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments
from oauth_scope import Scope
from user import User


def main(argv=[]):
    """
    This script gets the business accounts associated with a User.

    Strictly speaking, the READ_ADVERTISERS scope is neither
    necessary nor sufficient for this script to execute.
    However, obtaining the READ_ADVERTISERS scope is a good way to
    verify that the application is authorized to request the
    /v3/users/me/businesses endpoint.
    """
    parser = argparse.ArgumentParser(description="Get User Businesses")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # Note that the OAuth will fail if your application does not
    # have access to the scope that is required to access
    # linked business accounts.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_USERS, Scope.READ_ADVERTISERS])

    # use the access token to get information about the user
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    print("trying to get businesses...")
    user_me_businesses = user_me.get_businesses()
    if user_me_businesses:
        print(user_me_businesses)
    else:
        print("This account has no information on linked businesses.")


if __name__ == "__main__":
    main(sys.argv[1:])
