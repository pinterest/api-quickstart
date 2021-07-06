#!/usr/bin/env node
/**
 * Copying a board is not representative of typical user behavior on Pinterest.
 *
 * This script is intended to demonstrate how to use the API to developers,
 * and to provide functionality that might be convenient for developers.
 * For example, it might be used as part of a program to generate an
 * account to be used to test an API-based application.
 */
import {ArgumentParser} from 'argparse'

import {ApiConfig} from '../src/api_config.js'
import {common_arguments} from '../src/arguments.js'
import {SpamError} from '../src/api_common.js'

/**
 * This script is intended primarily for developers who need to create a test copy
 * of a board or all of the boards in an account. For each board, it copies the
 * board itself, all of the pins on the board, all of the board sections, and
 * all of the pins on each section. There are three intended use cases,
 * each with its own combination of arguments. All three use cases require at least
 * one access token, which may be created using the get_access_token.js script. All
 * three also require a source board identifier, which can be discovered using the
 * get_user_boards.js script.
 * 1. Copy a board within a single account. In this case, it is possible to use a
 *    single access token with the default name. Since each board in an account
 *    requires a unique name, the target board name must be specified. Here's an
 *    example of the command-line arguments for this use case:
 *      ./copy_board.js -b <board-id> -n 'test board 001'
 * 2. Copy a board from one account to another, which requires specifying one
 *    access token for the source account and one for the target account. See
 *    the comments at the top of the get_access_tokeh.js script for information
 *    about where access tokens are stored.
 *    For example:
 *      ./copy_board.js -b <board-id> -s source_account_token.json -t target_account_token.json
 * 3. Copy all of the boards from one account to another. This use case is designed
 *    to be used by developers to create a test account. This use case creates a lot of data,
 *    so it is advisable to use the dry-run argument to verify the pins and boards to be copied.
 *      ./copy_board.js --dry-run --all -s source_account_token.json -t target_account_token.json
 *      ./copy_board.js --all -s source_account_token.json -t target_account_token.json
 */
async function main (argv) {
  const parser = new ArgumentParser({
    description: "Copy one Board or all Boards"
  });
  parser.add_argument('-b', '--board-id', {help: 'destination board identifier'});
  parser.add_argument('-n', '--name', {help: 'target board name'});
  parser.add_argument('-s', '--source-access-token', {help: 'source access token name'});
  parser.add_argument('-t', '--target-access-token', {help: 'target access token name'});
  parser.add_argument('--all', {dest: 'all_boards', action: 'store_true', help: 'copy all boards from source to target'});
  parser.add_argument('--dry-run', {action: 'store_true', help: 'print changes but do not execute them'});
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // Check the combinations of arguments. The comment at the top of this function
  // describes the intended use cases.
  var args_error = null;
  if (args.target_access_token) {
    if (args.access_token) {
      args_error = 'generic access token may not be specified when using a target access token';
    }
    if (!args.source_access_token) {
      args_error = 'source access token is required when using a target access token';
    }
  } else {
    if (args.all_boards) {
      args_error = 'all boards option requires a target access token';
    }
    if (!args.name) {
      args_error = 'target board name is required when not using a target access token';
    }
    if (args.source_access_token && args.access_token) {
      args_error = 'generic access token may not be specified when using a source access token';
    }
  }

  if (args.all_boards && args.name) {
    args_error = 'the name and all options are mutually exclusive';
  }

  if (args.all_boards) {
    if (args.board_id) {
      args_error = 'the board-id and all options are mutually exclusive';
    }
  } else {
    if (!args.board_id) {
      args_error = 'board-id is a required argument when not copying all boards';
    }
  }

  if (args_error) {
    console.log(args_error);
    parser.print_usage();
    process.exit(1);
  }

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({verbosity: args.log_level, version: args.api_version});

  // imports that depend on the version of the API
  const {AccessToken} = await import(`../src/${api_config.version}/access_token.js`);
  const {Board} = await import(`../src/${api_config.version}/board.js`);
  const {Pin} = await import(`../src/${api_config.version}/pin.js`);
  const {Scope} = await import(`../src/${api_config.version}/oauth_scope.js`);
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // helper function to copy a pin
  const copy_pin = async function(pin, pin_data, target_board_id, {target_section_id=null}) {
    try {
      const pintype = pin_data.type;
      // Sometimes the board list operation will generate entities (e.g. "more ideas"
      // tiles) that resemble pins but can not be copied.
      if (!pintype || (pintype == 'pin')) {
        console.log('source pin:');
        Pin.print_summary(pin_data);
        const target_pin_data = await pin.create(pin_data, target_board_id,
                                                 {section: target_section_id});
        console.log('target pin:')
        Pin.print_summary(target_pin_data);
      } else {
        console.log("skipping pin because type is not 'pin'");
      }
    } catch (err) {
      if (err instanceof SpamError) {
        console.log('skipping pin because of spam exception');
      } else {
        throw err;
      }
    }
  }

  // Note: The same API configuration is used with both the source and target access tokens.
  var source_token;
  var target_token;
  if (args.source_access_token) {
    source_token = new AccessToken(api_config, {name: args.source_access_token});
  } else {
    source_token = new AccessToken(api_config, {name: args.access_token});
  }
  const source_token_scopes = [Scope.READ_PINS, Scope.READ_BOARDS];

  // Default to use the source token (same account) if the target token is not specified.
  const target_token_scopes = [Scope.WRITE_PINS,Scope.WRITE_BOARDS];
  if (args.target_access_token) {
    target_token = new AccessToken(api_config, {name: args.target_access_token});
    await target_token.fetch({scopes: target_token_scopes});
  } else {
    target_token = source_token; // use the same token...
    source_token_scopes.push(...target_token_scopes); // ...with all the scopes
  }

  await source_token.fetch({scopes:source_token_scopes}); // get the source token

  // This Pin object is reusable. The pin_id attribute is set when the
  // create method is called successfully.
  const target_pin = new Pin(null, api_config, target_token);

  var boards;
  var source_board;
  if (args.all_boards) { // copy all boards for the source user
    const user_me = new User('me', api_config, source_token);
    const user_me_data = await user_me.get();
    source_board = new Board(null, api_config, source_token); // board_id set in loop below
    boards = await user_me.get_boards(user_me_data, {});
  } else { // copy just the board designated by board_id
    source_board = new Board(args.board_id, api_config, source_token);
    const source_board_data = await source_board.get();
    boards = [source_board_data];
  }

  for await (let source_board_data of boards) {
    console.log('source board:');
    Board.print_summary(source_board_data);
    source_board.board_id = source_board_data.id;

    // Use different name, which is mandatory when using a single access token.
    // Change the name after the Board.print_summary with the source name.
    if (args.name) {
      console.log(`setting target board name to "${args.name}"`);
      source_board_data.name = args.name;
    }

    // This Board object is reusable. The board_id is set when the
    // create method is called successfully.
    const target_board = new Board(null, api_config, target_token);
    var target_board_data = null;
    if (args.dry_run) {
      console.log('dry-run: skipping attempt to create board:');
      Board.print_summary(source_board_data);
    } else {
      target_board_data = await target_board.create(source_board_data);
      console.log('target board:');
      Board.print_summary(target_board_data);
    }

    // copy board pins
    const pin_iterator = await source_board.get_pins();
    for await (let pin_data of pin_iterator) {
      if (args.dry_run) {
        console.log('dry-run: skipping attempt to create board pin:');
        Pin.print_summary(pin_data);
      } else {
        await copy_pin(target_pin, pin_data, target_board_data.id, {});
      }
    }

    // get and copy board sections
    const sections_iterator = await source_board.get_sections();
    var idx = 1;
    for await (let section_data of sections_iterator) {
      var target_section_data = null;
      if (args.dry_run) {
        console.log('dry-run: skipping attempt to create board section:');
        Board.print_section(section_data);
      } else {
        console.log(`source section #${idx}:`);
        Board.print_section(section_data);
        target_section_data = await target_board.create_section(section_data);
        console.log(`target section #${idx}:`);
        Board.print_section(target_section_data);
      }

      // copy board section pins
      const section_pin_iterator = await source_board.get_section_pins(section_data.id);
      for await (let pin_data of section_pin_iterator) {
        if (args.dry_run) {
          console.log('dry-run: skipping attempt to create board section pin:');
          Pin.print_summary(pin_data);
        } else {
          await copy_pin(target_pin, pin_data, target_board_data.id,
                         {target_section_id: target_section_data.id});
        }
      }
      idx++;
    }
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
