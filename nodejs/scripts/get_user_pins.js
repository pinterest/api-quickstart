#!/usr/bin/env node
import {ArgumentParser} from 'argparse'

import {ApiConfig} from '../src/api_config.js'
import {common_arguments} from '../src/arguments.js'

/**
 *  This script prints summary information for each of the pins in a
 *  User's profile. It demonstrates how to get paginated information from
 *  the Pinterest API.
 */
async function main (argv) {
  const parser = new ArgumentParser({
    description: "Get A User's Pins"
  });
  parser.add_argument('-ps', '--page-size',
                      {help: 'Boards per page', default: 25, type: 'int'});
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({verbosity: args.log_level, version: args.api_version});

  // imports that depend on the version of the API
  const {AccessToken} = await import(`../src/${api_config.version}/access_token.js`);
  const {Pin} = await import(`../src/${api_config.version}/pin.js`);
  const {Scope} = await import(`../src/${api_config.version}/oauth_scope.js`);
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {name: args.access_token});
  await access_token.fetch({scopes:[Scope.READ_USERS,Scope.READ_PINS]});

  // use the access token to get information about the user
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  // get information about all of the pins in the user's profile
  const pin_iterator = await user_me.get_pins(user_me_data,
                                              {query_parameters: {page_size: args.page_size}});
  await user_me.print_multiple(args.page_size, 'pin', Pin, pin_iterator);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
