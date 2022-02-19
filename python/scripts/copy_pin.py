#!/usr/bin/env python
#
# Copying a pin is not representative of typical user behavior on Pinterest.
#
# This script is intended to demonstrate how to use the API to developers,
# and to provide functionality that might be convenient for developers.
# For example, it might be used as part of a program to generate an
# account to be used to test an API-based application.
#
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments


def main(argv=[]):
    """
    This script copies a pin to a board, both of which are specified by identifiers
    that can be found using the get_user_pins.py and get_user_boards.py script.

    If a section identifier is specified in addition to a board identifier,
    this script will copy the pin to the board section. Section identifiers can be
    found using the get_board.py script. A section identifier may not be specified
    without a board identifier.
    """
    parser = argparse.ArgumentParser(description="Copy a Pin")
    parser.add_argument("-p", "--pin-id", required=True, help="source pin identifier")
    parser.add_argument("-m", "--media", help="media path or id")
    parser.add_argument(
        "-b", "--board-id", required=True, help="destination board identifier"
    )
    parser.add_argument("-s", "--section", help="destination board section")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from oauth_scope import Scope
    from pin import Pin

    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_PINS, Scope.WRITE_BOARDS, Scope.WRITE_PINS])

    pin = Pin(args.pin_id, api_config, access_token)
    pin_data = pin.get()
    print("source pin:")
    Pin.print_summary(pin_data)
    new_pin_data = pin.create(pin_data, args.board_id, args.section, args.media)
    print("new pin:")
    Pin.print_summary(new_pin_data)


if __name__ == "__main__":
    main(sys.argv[1:])
