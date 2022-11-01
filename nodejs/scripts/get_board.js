#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { Board } from '../src/board.js';
import { common_arguments } from '../src/arguments.js';
import { Pin } from '../src/pin.js';
import { Scope } from '../src/oauth_scope.js';

/**
 * This script prints the information associated with a pin. The pin identifier
 * my be obtained with the get_user_pins.py or get_board.py script.
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Get A Board'
  });
  parser.add_argument('-b', '--board-id', { required: true, help: 'board identifier' });
  parser.add_argument('--pins', { action: 'store_true', help: 'Get the Pins for the Board' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  const scopes = [Scope.READ_USERS, Scope.READ_BOARDS];
  if (args.pins) {
    scopes.push(Scope.READ_PINS);
  }
  await access_token.fetch({ scopes: scopes });

  const board = new Board(args.board_id, api_config, access_token);
  const board_data = await board.get();
  Board.print_summary(board_data);

  if (args.pins) {
    const pin_iterator = await board.get_pins();
    for await (const pin_data of pin_iterator) {
      // ignore pins in sections for now. they will be printed for each section
      if (pin_data.board_section_id) {
        continue;
      }
      Pin.print_summary(pin_data);
    }
  }

  const section_iterator = await board.get_sections();
  for await (const section_data of section_iterator) {
    Board.print_section(section_data);
    if (args.pins) {
      const pin_iterator = await board.get_section_pins(section_data.id);
      for await (const pin_data of pin_iterator) {
        Pin.print_summary(pin_data);
      }
    }
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
