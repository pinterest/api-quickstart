#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';

/**
 * This script saves a pin to a board. This action is informally
 * called "Pinning."
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Save a Pin to a Board'
  });
  parser.add_argument('-p', '--pin-id', { required: true, help: 'pin identifier' });
  parser.add_argument('-b', '--board-id', { required: true, help: 'board identifier' });
  parser.add_argument('-s', '--section', { help: 'board section identifier' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level, version: args.api_version });

  // imports that depend on the version of the API
  const { AccessToken } = await import(`../src/${api_config.version}/access_token.js`);
  const { Board } = await import(`../src/${api_config.version}/board.js`);
  const { Pin } = await import(`../src/${api_config.version}/pin.js`);
  const { Scope } = await import(`../src/${api_config.version}/oauth_scope.js`);

  const access_token = new AccessToken(api_config, { name: args.access_token });
  // TODO: is READ_USERS necessary?
  const scopes = [Scope.READ_USERS, Scope.READ_PINS, Scope.WRITE_PINS, Scope.READ_BOARDS, Scope.WRITE_BOARDS];

  await access_token.fetch({ scopes: scopes });

  const pin = new Pin(args.pin_id, api_config, access_token);

  const saved_pin_data = await pin.save(args.board_id, { section: args.section });
  console.log('saved pin');
  Pin.print_summary(saved_pin_data);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
