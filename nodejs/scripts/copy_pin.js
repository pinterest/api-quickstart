#!/usr/bin/env node
/**
 * Copying a pin is not representative of typical user behavior on Pinterest.
 *
 * This script is intended to demonstrate how to use the API to developers,
 * and to provide functionality that might be convenient for developers.
 * For example, it might be used as part of a program to generate an
 * account to be used to test an API-based application.
 */
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Pin } from '../src/pin.js';
import { Scope } from '../src/oauth_scope.js';

/**
 * This script copies a pin to a board, both of which are specified by identifiers
 * that can be found using the get_user_pins.py and get_user_boards.py script.
 *
 * If a section identifier is specified in addition to a board identifier,
 * this script will copy the pin to the board section. Section identifiers can be
 * found using the get_board.py script. A section identifier may not be specified
 * without a board identifier.
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Copy A Pin'
  });
  parser.add_argument('-p', '--pin-id', { required: true, help: 'source pin identifier' });
  parser.add_argument('-b', '--board-id', { required: true, help: 'destination board identifier' });
  parser.add_argument('-m', '--media', { help: 'media path or id' });
  parser.add_argument('-s', '--section', { help: 'destination board section' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  await access_token.fetch({ scopes: [Scope.READ_PINS, Scope.WRITE_BOARDS, Scope.WRITE_PINS] });

  const pin = new Pin(args.pin_id, api_config, access_token);
  const pin_data = await pin.get();
  console.log('source pin:');
  Pin.print_summary(pin_data);
  const new_pin_data = await pin.create(pin_data, args.board_id, {
    section: args.section,
    media: args.media
  });
  console.log('new pin:');
  Pin.print_summary(new_pin_data);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
