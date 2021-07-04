#!/usr/bin/env node
import {ArgumentParser} from 'argparse'

import {AccessToken} from '../src/access_token.js'
import {ApiConfig} from '../src/api_config.js'

/**
 *  This script prints summary information for each of the boards in a
 *  User's profile. It demonstrates how to get paginated information from
 *  the Pinterest API.
 */
async function main (argv) {
  const parser = new ArgumentParser({
    description: "Get A User's Boards"
  });
  parser.add_argument('-ps', '--page-size',
                      {help: 'Boards per page', default: 25, type: 'int'});
  parser.add_argument('--include-empty',
                      {help: 'Include empty boards?', dest: 'include_empty', action: 'store_true'});
  parser.add_argument('--no-include-empty',
                      {dest: 'include_empty', default: true, action: 'store_false'});
  parser.add_argument('--include-archived',
                      {help: 'Include archived boards?', dest: 'include_archived', action: 'store_true'});
  parser.add_argument('--no-include-archived',
                      {dest: 'include_archived', default: false, action: 'store_false'});
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();
  api_config.verbosity = 2;

  // imports that depend on the version of the API
  const {Board} = await import(`../src/${api_config.version}/board.js`);
  const {Scope} = await import(`../src/${api_config.version}/oauth_scope.js`);
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {});
  var scopes = null // use the default set of scopes
  await access_token.fetch({scopes:[Scope.READ_USERS,Scope.READ_BOARDS]});

  // use the access token to get information about the user
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  // get information about all of the boards in the user's profile
  const query_parameters = {
    'page_size': args.page_size,
    'include_empty': args.include_empty,
    'include_archived': args.include_archived
  };
  const board_iterator = await user_me.get_boards(user_me_data, {query_parameters: query_parameters});
  await user_me.print_multiple(args.page_size, 'board', Board, board_iterator);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}