#!/usr/bin/env python
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from access_token import AccessToken
from oauth_scope import Scope

def main(argv=[]):
    def positive_integer(number):
        ivalue = int(number)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f'{number} must be a positive integer')
        return ivalue

    parser = argparse.ArgumentParser(description="Get A User's Pins")
    parser.add_argument('-ps', '--page-size', help='Pins per page',
                        default=25, type=positive_integer)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 2

    # imports that depend on the version of the API
    from pin import Pin
    from user import User

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config)
    access_token.fetch()

    # use the access token to get information about the user
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    pin_iterator = user_me.get_pins(user_me_data,
                                    query_parameters={'page_size': args.page_size})
    user_me.print_multiple(args.page_size, 'pin', Pin, pin_iterator)

if __name__ == '__main__':
    main(sys.argv[1:])
