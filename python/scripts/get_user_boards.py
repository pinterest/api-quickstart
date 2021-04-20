#!/usr/bin/env python
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_config import ApiConfig
from api_object import ApiObject
from access_token import AccessToken
from board import Board
from oauth_scope import Scope
from user import User

def main(argv=[]):
    def positive_integer(number):
        ivalue = int(number)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f'{number} must be a positive integer')
        return ivalue

    parser = argparse.ArgumentParser(description="Get A User's Boards")
    parser.add_argument('-ps', '--page-size', help='Boards per page',
                        default=25, type=positive_integer)
    # include_empty is an example of an API parameter
    parser.add_argument('--include-empty', help='Include empty boards?', dest='include_empty', action='store_true')
    parser.add_argument('--no-include-empty', dest='include_empty', action='store_false')
    parser.set_defaults(include_empty=True)
    parser.add_argument('--include-archived', help='Include archived boards?', dest='include_archived', action='store_true')
    parser.add_argument('--no-include-archived', dest='include_archived', action='store_false')
    parser.set_defaults(include_archived=False)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 2

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config)
    access_token.fetch()

    # use the access token to get information about the user
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    query_parameters={'page_size': args.page_size,
                      'include_empty': args.include_empty,
                      'include_archived': args.include_archived,
                      }
    board_iterator = user_me.get_boards(user_me_data, query_parameters)
    ApiObject.print_multiple(args.page_size, 'board', Board, board_iterator)

if __name__ == '__main__':
    main(sys.argv[1:])
