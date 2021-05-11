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
    parser.add_argument('-b', '--board-id', required=True, help='source board identifier')
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
        print('the name and all options are mutually exclusive')
        exit(1)

    if args.all_boards and args.board_id:
        print('the board-id and all options are mutually exclusive')
        exit(1)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig()
    api_config.verbosity = 2

    # imports that depend on the version of the API
    from board import Board
    from pin import Pin

    def copy_pin(pin, pin_data, target_board_id, target_section_id=None):
        try:
            if pin_data['type'] == 'pin':
                print('source pin:')
                Pin.print_summary(pin_data)
                new_pin_data = pin.create(pin_data, target_board_id, target_section_id)
                print('new pin:')
                Pin.print_summary(new_pin_data)
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

    board = Board(args.board_id, api_config, source_token)
    board_data = board.get()
    print('source board:')
    Board.print_summary(board_data)

    # option: use different name, which should be mandatory when using
    # a single access token
    if args.name:
        print('setting target board name to "' + args.name + '"')
        board_data['name'] = args.name

    new_board = Board(None, api_config, target_token) # board_id set by create
    if args.dry_run:
        print('dry-run: skipping attempt to create board:')
        Board.print_summary(board_data)
    else:
        new_board_data = new_board.create(board_data)
        print('new board:')
        Board.print_summary(new_board_data)

    # copy board pins
    for pin_data in board.get_pins():
        if args.dry_run:
            print('dry-run: skipping attempt to create board pin:')
            Pin.print_summary(pin_data)
        else:
            copy_pin(target_pin, pin_data, new_board_data['id'])

    sections_iterator = board.get_sections()
    for idx, section_data in enumerate(sections_iterator):
        if args.dry_run:
            print('dry-run: skipping attempt to create board section:')
            Board.print_section(section_data)
        else:
            print(f'source section #{idx}:')
            Board.print_section(section_data)
            new_section_data = new_board.create_section(section_data)
            print(f'new section #{idx}:')
            Board.print_section(new_section_data)
        
        # copy board section pins
        for pin_data in board.get_section_pins(section_data['id']):
            if args.dry_run:
                print('dry-run: skipping attempt to create board section pin:')
                Pin.print_summary(pin_data)
            else:
                copy_pin(target_pin, pin_data, new_board_data['id'], new_section_data['id'])

if __name__ == '__main__':
    main(sys.argv[1:])
