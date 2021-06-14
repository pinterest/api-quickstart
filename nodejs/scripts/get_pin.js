#!/usr/bin/env node
import {ArgumentParser} from 'argparse'

import {AccessToken} from '../src/access_token.js'
import {ApiConfig} from '../src/api_config.js'
import {Scope} from '../src/oauth_scope.js'

/**
 * This script prints the information associate with a pin. The pin identifier
 * my be obtained with the get_user_pins.py or get_board.py script.
 */
async function main (argv) {
  const parser = new ArgumentParser({
    description: "Get A Pin"
  });
  parser.add_argument('-p', '--pin-id', {required: true, help: 'pin identifier'});
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();
  api_config.verbosity = 2;

  // imports that depend on the version of the API
  const {Pin} = await import(`../src/${api_config.version}/pin.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {});
  await access_token.fetch({scopes:[Scope.READ_PINS]});

  const pin = new Pin(args.pin_id, api_config, access_token);
  const pin_data = await pin.get();
  Pin.print_summary(pin_data);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
