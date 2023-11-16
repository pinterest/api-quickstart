#!/usr/bin/env python
#
# Deleting a board is not a very common action for Pinners, but is
# useful for developers who need to clean up test pins, boards, and accounts.
#
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments
from board import Board
from oauth_scope import Scope
from user import User
from utils import input_one_of


def main(argv=[]):
    """
    This script is intended primarily for developers who need to delete boards
    that were used for test purposes. The script requests input that verifies
    the intent to permanantly delete data.
    """
    parser = argparse.ArgumentParser(description="Delete one Board or all Boards")
    parser.add_argument("-b", "--board-id", help="identifier of board to be deleted")
    parser.add_argument(
        "--all-boards", action="store_true", help="delete all boards from the account"
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    # Check the arguments: need specify exactly one of board_id and all_boards.
    if not (bool(args.board_id) ^ bool(args.all_boards)):
        parser.error("specify exactly one of --board-id and --all-boards")

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    # get access token
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_USERS, Scope.READ_BOARDS, Scope.WRITE_BOARDS])

    if args.all_boards:  # delete all boards for the user
        user = User(api_config, access_token)
        user_data = user.get()
        boards = user.get_boards(user_data)
        confirmation = f"Delete all boards for {user_data['username']}"
    else:  # copy just the board designated by board_id
        deletion_board = Board(args.board_id, api_config, access_token)
        board_data = deletion_board.get()
        confirmation = f"Delete this board: {Board.text_id(board_data)}"
        boards = [board_data]

    try:
        print(
            "WARNING: This script permanently deletes pins and boards from Pinterest!"
        )
        print(
            "To acknowledge this warning, "
            "enter the following information at the prompt:"
        )
        print("  ", confirmation)
        confirmation_response = input("> ").strip()
    except KeyboardInterrupt:
        print("...Canceling deletion.")
        exit()

    if confirmation != confirmation_response:
        print("Deletion not confirmed. Exiting.")
        exit()

    deletion_board = Board(None, api_config, access_token)  # board_id set in loop below
    for board_data in boards:

        # one final check before deletion
        Board.print_summary(board_data)
        if "yes" != input_one_of(
            f"Delete board: {Board.text_id(board_data)}? ", ["yes", "no"], "yes"
        ):
            continue

        deletion_board.board_id = board_data["id"]
        deletion_board.delete()


# If this script is being called from the command line, call the main function
# with the arguments. The other use case is to call main() from an integration test.
if __name__ == "__main__":
    main(sys.argv[1:])
