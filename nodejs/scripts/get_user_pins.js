#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Pin } from '../src/pin.js';
import { Scope } from '../src/oauth_scope.js';
import { User } from '../src/user.js';

/**
 *  This script prints summary information for each of the pins in a
 *  User's profile. It demonstrates how to get paginated information from
 *  the Pinterest API.
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: "Get A User's Pins"
  });
  parser.add_argument('-ps', '--page-size',
    { help: 'Boards per page', default: 25, type: 'int' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  await access_token.fetch({
    scopes: [
      Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS]
  });

  // use the access token to get information about the user
  const user = new User(api_config, access_token);
  const user_data = await user.get();
  user.print_summary(user_data);

  // get information about all of the pins in the user's profile
  const pin_iterator = await user.get_pins(user_data,
    { query_parameters: { page_size: args.page_size } });
  await user.print_multiple(args.page_size, 'pin', Pin, pin_iterator);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
