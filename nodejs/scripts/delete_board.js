#!/usr/bin/env node
/**
 * Deleting a board is not a very common action for Pinners, but is
 * useful for developers who need to clean up test pins, boards, and accounts.
 */
import {ArgumentParser} from 'argparse'

import {AccessToken} from '../src/access_token.js'
import {ApiConfig} from '../src/api_config.js'
import {Input} from '../src/utils.js'
import {Scope} from '../src/oauth_scope.js'

/**
 * This script is intended primarily for developers who need to delete boards
 * that were used for test purposes. The script requests input that verifies
 * the intent to permanantly delete data.
 */
async function main (argv) {
  const parser = new ArgumentParser({
    description: "Delete on Board or all Boards"
  });
  parser.add_argument('-b', '--board-id', {help: 'board identifier'});
  parser.add_argument('--all-boards', {action: 'store_true', help: 'delete all boards from the account'});
  const args = parser.parse_args(argv);

  // Check the arguments: need specify exactly one of board_id and all_boards.
  if (!(Boolean(args.board_id) ^ Boolean(args.all_boards))) {
    parser.print_usage();
    console.log('specify exactly one of --board-id or --all-boards');
    process.exit(1);
  }

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();
  api_config.verbosity = 2;

  // imports that depend on the version of the API
  const {Board} = await import(`../src/${api_config.version}/board.js`);
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // get access token
  const access_token = new AccessToken(api_config, {});
  await access_token.fetch({scopes:[Scope.READ_USERS,Scope.READ_BOARDS,Scope.WRITE_BOARDS]});

  var boards;
  var confirmation = null;
  if (args.all_boards) { // delete all boards for the user
    const user_me = new User('me', api_config, access_token);
    const user_me_data = await user_me.get();
    boards = await user_me.get_boards(user_me_data, {});
    confirmation = 'Delete all boards for ' + user_me_data.full_name;
  } else { // copy just the board designated by board_id
    const deletion_board = new Board(args.board_id, api_config, access_token);
    const board_data = await deletion_board.get();
    confirmation = 'Delete the board with URL ' + board_data.url;
    boards = [board_data];
  }

  console.log('WARNING: This script permanently deletes pins and boards from Pinterest!');
  console.log('To acknowledge this warning, enter the following information at the prompt:');
  console.log('  ', confirmation);
  const input = new Input();
  const confirmation_response = await input.get('> ');
  if (confirmation != confirmation_response.trim()) {
    console.log('Deletion not confirmed. Exiting.');
    process.exit(2);
  }

  // board_id set in loop below
  const deletion_board = new Board(null, api_config, access_token);
  for await (let board_data of boards) {
    // one final check before deletion
    Board.print_summary(board_data);
    if ('yes' != await input.one_of(`Delete board at ${board_data.url}? `,
                                    ['yes', 'no'], 'yes')) {
      continue;
    }
    deletion_board.board_id = board_data.id;
    await deletion_board.delete();
  }

  input.close(); // so that process can exit
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
