#!/usr/bin/env python
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from access_token import AccessToken
from oauth_scope import Scope

def main(argv=[]):
    """
    This script prints the information associate with a pin. The pin identifier
    my be obtained with the get_user_pins.py or get_board.py script.
    """
    parser = argparse.ArgumentParser(description='Get a Pin')
    parser.add_argument('-p', '--pin-id', required=True, help='pin identifier')
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 3

    # imports that depend on the version of the API
    from pin import Pin

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config)
    access_token.fetch(scopes=[Scope.READ_PINS])

    pin = Pin(args.pin_id, api_config, access_token)
    pin_data = pin.get()
    pin.print_summary(pin_data)

if __name__ == '__main__':
    main(sys.argv[1:])
