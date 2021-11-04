#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments, positive_integer


def main(argv=[]):
    """
    This script prints summary information for each of the pins in a
    User's profile. It demonstrates how to get paginated information from
    the Pinterest API.
    """
    parser = argparse.ArgumentParser(description="Get A User's Pins")
    parser.add_argument(
        "-ps", "--page-size", help="Pins per page", default=25, type=positive_integer
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from oauth_scope import Scope
    from pin import Pin
    from user import User

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS])

    # use the access token to get information about the user
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()

    # get information about all of the pins in the user's profile
    pin_iterator = user_me.get_pins(
        user_me_data, query_parameters={"page_size": args.page_size}
    )
    user_me.print_multiple(args.page_size, "pin", Pin, pin_iterator)


if __name__ == "__main__":
    main(sys.argv[1:])
