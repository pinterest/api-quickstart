#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments, positive_integer
from board import Board
from oauth_scope import Scope
from user import User


def main(argv=[]):
    """
    This script prints summary information for each of the boards in a
    User's profile. It demonstrates how to get paginated information from
    the Pinterest API.
    """

    parser = argparse.ArgumentParser(description="Get A User's Boards")
    parser.add_argument(
        "-ps", "--page-size", help="Boards per page", default=25, type=positive_integer
    )
    # include_empty is an example of an API parameter
    parser.add_argument(
        "--include-empty",
        help="Include empty boards?",
        dest="include_empty",
        action="store_true",
    )
    parser.add_argument(
        "--no-include-empty", dest="include_empty", action="store_false"
    )
    parser.add_argument(
        "--include-archived",
        help="Include archived boards?",
        dest="include_archived",
        action="store_true",
    )
    parser.add_argument(
        "--no-include-archived", dest="include_archived", action="store_false"
    )
    parser.set_defaults(include_archived=False)
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_USERS, Scope.READ_BOARDS])

    # use the access token to get information about the user
    user = User(api_config, access_token)
    user_data = user.get()

    # get information about all of the boards in the user's profile
    query_parameters = {"page_size": args.page_size}
    if args.include_empty:
        query_parameters["include_empty"] = args.include_empty
    if args.include_archived:
        query_parameters["include_archived"] = args.include_archived
    board_iterator = user.get_boards(user_data, query_parameters)
    user.print_multiple(args.page_size, "board", Board, board_iterator)


if __name__ == "__main__":
    main(sys.argv[1:])
