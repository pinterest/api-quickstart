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

from api_config import ApiConfig
from api_config import SpamException
from access_token import AccessToken
from oauth_scope import Scope

def main(argv=[]):
    parser = argparse.ArgumentParser(description='Copy a Board')
    parser.add_argument('-b', '--board-id', help='source board identifier')
    parser.add_argument('-n', '--name', help='target board name')
    parser.add_argument('-s', '--source-access-token', help='source access token name')
    parser.add_argument('-t', '--target-access-token', help='target access token name')
    parser.add_argument('--all', dest='all_boards', action='store_true', help='copy all boards from source to target')
    parser.add_argument('--dry-run', action='store_true', help='print changes but do not execute them')
    args = parser.parse_args(argv)

    if args.target_access_token:
        if not args.source_access_token:
            parser.print_usage()
            print('source access token is required when using a target access token')
            exit(1)
    else:
        if args.all_boards:
            parser.print_usage()
            print('all boards option requires a target access token')
            exit(1)
        if not args.name:
            parser.print_usage()
            print('target board name is required when not using a target access token')
            exit(1)

    if args.all_boards and args.name:
        parser.print_usage()
        print('the name and all options are mutually exclusive')
        exit(1)

    if args.all_boards:
        if args.board_id:
            parser.print_usage()
            print('the board-id and all options are mutually exclusive')
            exit(1)
    else:
        if not args.board_id:
            parser.print_usage()
            print('board-id is a required argument when not copying all boards')
            exit(1)


    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 2

    # imports that depend on the version of the API
    from board import Board
    from pin import Pin
    from user import User

    def copy_pin(pin, pin_data, target_board_id, target_section_id=None):
        try:
            if pin_data['type'] == 'pin':
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

    # Note: The same API configuration is used with both the
    # source and target access tokens.

    if args.source_access_token:
        source_token = AccessToken(api_config, name=args.source_access_token)
    else:
        source_token = AccessToken(api_config)
    source_token.fetch(scopes=[Scope.READ_PINS, Scope.READ_BOARDS]) # get the token

    if args.target_access_token:
        target_token = AccessToken(api_config, name=args.target_access_token)
        target_token.fetch(scopes=[Scope.WRITE_PINS,Scope.WRITE_BOARDS]) # TODO: need write scope?
    else:
        target_token = source_token # already have the token

    target_pin = Pin(None, api_config, target_token) # pin_id set by create

    if args.all_boards: # copy all boards for the source user
        user_me = User('me', api_config, source_token)
        user_me_data = user_me.get()
        boards = user_me.get_boards(user_me_data)
        source_board = Board(None, api_config, source_token) # board_id set in loop below
    else: # copy just the board designated by board_id
        source_board = Board(args.board_id, api_config, source_token)
        source_board_data = source_board.get()
        # use different name, which is mandatory when using a single access token
        if args.name:
            print('setting target board name to "' + args.name + '"')
            source_board_data['name'] = args.name
        boards = [source_board_data]

    for source_board_data in boards:

        print('source board:')
        Board.print_summary(source_board_data)
        source_board.board_id = source_board_data['id']

        target_board = Board(None, api_config, target_token) # board_id set by create
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

if __name__ == '__main__':
    main(sys.argv[1:])
