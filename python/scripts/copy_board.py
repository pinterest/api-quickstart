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
    parser.add_argument('-b', '--board_id', required=True, help='source board identifier')
    parser.add_argument('-n', '--name', required=True, help='target board name')
    parser.add_argument('-s', '--source_access_token', help='source access token name')
    parser.add_argument('-t', '--target_access_token', help='target access token name')
    args = parser.parse_args(argv)

    if args.target_access_token:
        if not args.source_access_token:
            print('source access token is required when using a target access token')
            exit(1)
        print('oops! target access token is not yet supported. :-p')
        exit(2)
    else:
        if not args.name:
            print('target board name is required when not using a target access token')

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

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config)
    access_token.fetch(scopes=[Scope.READ_PINS]) # TODO: need write scope?

    # need to think about how the Pin object should work in this case...
    pin_for_api = Pin(0, api_config, access_token)

    board = Board(args.board_id, api_config, access_token)
    board_data = board.get()
    print('source board:')
    board.print_summary(board_data)

    # option: use different name, which should be mandatory when using
    # a single access token
    if args.name:
        print('setting target board name to "' + args.name + '"')
        board_data['name'] = args.name

    # TODO: support separate access tokens for the source and destination boards
    new_board_data = board.create(board_data)
    new_board = Board(new_board_data['id'], api_config, access_token)
    print('new board:')
    new_board.print_summary(new_board_data)

    # copy board pins
    for pin_data in board.get_pins():
        copy_pin(pin_for_api, pin_data, new_board_data['id'])

    sections_iterator = board.get_sections()
    for idx, section_data in enumerate(sections_iterator):
        print(f'source section #{idx}:')
        board.print_section(section_data)
        new_section_data = new_board.create_section(section_data)
        print(f'new section #{idx}:')
        new_board.print_section(new_section_data)
        
        # copy board section pins
        for pin_data in board.get_section_pins(section_data['id']):
            copy_pin(pin_for_api, pin_data, new_board_data['id'], new_section_data['id'])

if __name__ == '__main__':
    main(sys.argv[1:])
