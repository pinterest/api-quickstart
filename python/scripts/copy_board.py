#!/usr/bin/env python
#
# Copying a board is not representative of typical user behavior on Pinterest.
#
# This script is intended to demonstrate how to use the API to developers,
# and to provide functionality that might be convenient for developers.
# For example, it might be used as part of a program to generate an
# account to be used to test an API-based application.
#
from os.path import dirname, abspath, join
import argparse
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from api_common import SpamException
from api_config import ApiConfig
from access_token import AccessToken

def main(argv=[]):
    """
    This script is intended primarily for developers who need to create a test copy
    of a board or all of the boards in an account. For each board, it copies the
    board itself, all of the pins on the board, all of the board sections, and
    all of the pins on each section. There are three intended use cases,
    each with its own combination of arguments. All three use cases require at least
    one access token, which may be created using the get_access_token.py script. All
    three also require a source board identifier, which can be discovered using the
    get_user_boards.py script.
    1. Copy a board within a single account. In this case, it is possible to use a
       single access token with the default name. Since each board in an account
       requires a unique name, the target board name must be specified. Here's an
       example of the command-line arguments for this use case:
         ./copy_board.py -b <board-id> -n 'test board 001'
    2. Copy a board from one account to another, which requires specifying one
       access token for the source account and one for the target account. See
       the comments at the top of the get_access_tokeh.py script for information
       about where access tokens are stored.
       For example:
         ./copy_board.py -b <board-id> -s source_account_token.json -t target_account_token.json
    3. Copy all of the boards from one account to another. This use case is designed
       to be used by developers to create a test account. This use case creates a lot of data,
       so it is advisable to use the dry-run argument to verify the pins and boards to be copied.
         ./copy_board.py --dry-run --all -s source_account_token.json -t target_account_token.json
         ./copy_board.py --all -s source_account_token.json -t target_account_token.json
    """
    parser = argparse.ArgumentParser(description='Copy one Board or all Boards')
    parser.add_argument('-b', '--board-id', help='source board identifier')
    parser.add_argument('-n', '--name', help='target board name')
    parser.add_argument('-s', '--source-access-token', help='source access token name')
    parser.add_argument('-t', '--target-access-token', help='target access token name')
    parser.add_argument('--all', dest='all_boards', action='store_true', help='copy all boards from source to target')
    parser.add_argument('--dry-run', action='store_true', help='print changes but do not execute them')
    args = parser.parse_args(argv)

    # Check the combinations of arguments. The comment at the top of this function
    # describes the intended use cases.
    args_error = None
    if args.target_access_token:
        if not args.source_access_token:
            args_error = 'source access token is required when using a target access token'
    else:
        if args.all_boards:
            args_error = 'all boards option requires a target access token'
        if not args.name:
            args_error = 'target board name is required when not using a target access token'

    if args.all_boards and args.name:
        args_error = 'the name and all options are mutually exclusive'

    if args.all_boards:
        if args.board_id:
            args_error = 'the board-id and all options are mutually exclusive'
    else:
        if not args.board_id:
            args_error = 'board-id is a required argument when not copying all boards'

    # In case of an argument error, print an appropriate message, usage information, and exit.
    if args_error:
        print(args_error)
        parser.print_usage()
        exit(1)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 2

    # imports that depend on the version of the API
    from board import Board
    from oauth_scope import Scope
    from pin import Pin
    from user import User

    # helper function to copy a pin
    def copy_pin(pin, pin_data, target_board_id, target_section_id=None):
        try:
            pintype = pin_data.get('type')
            # Sometimes the board list operation will generate entities (e.g. "more ideas"
            # tiles) that resemble pins but can not be copied.
            if not pintype or pintype == 'pin':
                print('source pin:')
                Pin.print_summary(pin_data)
                target_pin_data = pin.create(pin_data, target_board_id, target_section_id)
                print('target pin:')
                Pin.print_summary(target_pin_data)
            else:
                print("skipping pin because type is not 'pin'")
                Pin.print_summary(pin_data)
        except SpamException:
            print('skipping pin because of spam exception')

    # Note: The same API configuration is used with both the source and target access tokens.
    if args.source_access_token:
        source_token = AccessToken(api_config, name=args.source_access_token)
    else:
        source_token = AccessToken(api_config)
    source_token_scopes = [Scope.READ_PINS, Scope.READ_BOARDS]

    # Default to use the source token (same account) if the target token is not specified.
    target_token_scopes = [Scope.WRITE_PINS,Scope.WRITE_BOARDS]
    if args.target_access_token:
        target_token = AccessToken(api_config, name=args.target_access_token)
        target_token.fetch(scopes=target_token_scopes)
    else:
        target_token = source_token # use the same token...
        source_token_scopes += target_token_scopes # ...with all scopes

    source_token.fetch(scopes=source_token_scopes) # get the source token

    # This Pin object is reusable. The pin_id attribute is set when the
    # create method is called successfully.
    target_pin = Pin(None, api_config, target_token)

    if args.all_boards: # copy all boards for the source user
        user_me = User('me', api_config, source_token)
        user_me_data = user_me.get()
        boards = user_me.get_boards(user_me_data)
        source_board = Board(None, api_config, source_token) # board_id set in loop below
    else: # copy just the board designated by board_id
        source_board = Board(args.board_id, api_config, source_token)
        source_board_data = source_board.get()
        boards = [source_board_data]

    for source_board_data in boards:

        print('source board:')
        Board.print_summary(source_board_data)
        source_board.board_id = source_board_data['id']

        # Use different name, which is mandatory when using a single access token.
        # Change the name after the Board.print_summary with the source name.
        if args.name:
            print('setting target board name to "' + args.name + '"')
            source_board_data['name'] = args.name

        # This Board object is reusable. The board_id is set when the
        # create method is called successfully.
        target_board = Board(None, api_config, target_token)
        if args.dry_run:
            print('dry-run: skipping attempt to create board:')
            Board.print_summary(source_board_data)
        else:
            target_board_data = target_board.create(source_board_data)
            print('target board:')
            Board.print_summary(target_board_data)

        # copy board pins
        for pin_data in source_board.get_pins():
            if args.dry_run:
                print('dry-run: skipping attempt to create board pin:')
                Pin.print_summary(pin_data)
            else:
                copy_pin(target_pin, pin_data, target_board_data['id'])

        # get and copy board sections
        sections_iterator = source_board.get_sections()
        for idx, section_data in enumerate(sections_iterator):
            if args.dry_run:
                print('dry-run: skipping attempt to create board section:')
                Board.print_section(section_data)
            else:
                print(f'source section #{idx}:')
                Board.print_section(section_data)
                target_section_data = target_board.create_section(section_data)
                print(f'target section #{idx}:')
                Board.print_section(target_section_data)

            # copy board section pins
            for pin_data in source_board.get_section_pins(section_data['id']):
                if args.dry_run:
                    print('dry-run: skipping attempt to create board section pin:')
                    Pin.print_summary(pin_data)
                else:
                    copy_pin(target_pin, pin_data, target_board_data['id'], target_section_data['id'])

# If this script is being called from the command line, call the main function
# with the arguments. The other use case is to call main() from an integration test.
if __name__ == '__main__':
    main(sys.argv[1:])
