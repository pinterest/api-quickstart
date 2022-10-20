#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments
from oauth_scope import Scope
from pin import Pin


def main(argv=[]):
    """
    This script prints the information associated with a pin. The pin identifier
    my be obtained with the get_user_pins.py or get_board.py script.
    """
    parser = argparse.ArgumentParser(description="Get a Pin")
    parser.add_argument("-p", "--pin-id", required=True, help="pin identifier")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_PINS])

    pin = Pin(args.pin_id, api_config, access_token)
    pin_data = pin.get()
    pin.print_summary(pin_data)


if __name__ == "__main__":
    main(sys.argv[1:])
