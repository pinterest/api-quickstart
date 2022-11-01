#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))


from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments
from board import Board
from oauth_scope import Scope
from pin import Pin


def main(argv=[]):
    """
    This script prints the information associated with a board. The board identifier
    may be obtained with the get_user_boards script. If the board has any sections,
    the script will print information about them.

    Specify the --pins argument to print information about each pin on the board
    and its sections.
    """
    parser = argparse.ArgumentParser(description="Get a Board")
    parser.add_argument("-b", "--board-id", required=True, help="board identifier")
    parser.add_argument(
        "--pins", action="store_true", help="Get the Pins for the Board"
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    scopes = [Scope.READ_USERS, Scope.READ_BOARDS]
    if args.pins:
        scopes.append(Scope.READ_PINS)
    access_token.fetch(scopes=scopes)

    board = Board(args.board_id, api_config, access_token)
    board_data = board.get()
    board.print_summary(board_data)

    if args.pins:
        for pin_data in board.get_pins():
            # ignore pins in sections for now. they will be printed for each section
            if not pin_data.get("board_section_id"):
                Pin.print_summary(pin_data)

    for section_data in board.get_sections():
        board.print_section(section_data)
        if args.pins:
            for pin_data in board.get_section_pins(section_data["id"]):
                Pin.print_summary(pin_data)


if __name__ == "__main__":
    main(sys.argv[1:])
