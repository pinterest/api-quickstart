#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';

/**
 * This script refreshes an access token originally created by using the
 * the get_access_token.py script with the --write argument. The new access
 * token may be printed with the --cleartext option.
 */
async function main(argv) {
  const parser = new ArgumentParser({ description: 'Refresh Pinterest OAuth token' });
  parser.add_argument('-ct', '--cleartext', { action: 'store_true', help: 'print the token in clear text' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  const access_token = new AccessToken(api_config, { name: args.access_token });
  access_token.read();
  await access_token.refresh();

  // Note: It is best practice not to print credentials in clear text.
  // Pinterest engineers asked for this capability to make it easier to support partners.
  if (args.cleartext) {
    console.warn('Please keep clear text tokens secure!');
    console.log('clear text access token after refresh:', access_token.access_token);
  }
  console.log('hashed access token after refresh:', access_token.hashed());

  console.log('writing access token');
  access_token.write();
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
