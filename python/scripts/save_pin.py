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
    This script saves a pin to a board. This action is informally
    called "Pinning."
    """
    parser = argparse.ArgumentParser(description="Save a Pin to a Board")
    parser.add_argument("-p", "--pin-id", required=True, help="pin identifier")
    parser.add_argument("-b", "--board-id", required=True, help="board identifier")
    parser.add_argument(
        "-s", "--section", required=False, help="board section identifier"
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    access_token = AccessToken(api_config, name=args.access_token)
    scopes = [Scope.READ_PINS, Scope.WRITE_PINS, Scope.READ_BOARDS, Scope.WRITE_BOARDS]
    access_token.fetch(scopes=scopes)

    pin = Pin(args.pin_id, api_config, access_token)
    saved_pin_data = pin.save(args.board_id, section=args.section)
    pin.print_summary(saved_pin_data)


if __name__ == "__main__":
    main(sys.argv[1:])
