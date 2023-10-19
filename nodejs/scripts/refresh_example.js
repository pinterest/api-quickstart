#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Scope } from '../src/oauth_scope.js';
import { User } from '../src/user.js';

/**
 * This script was written primarily as a way for folks at Pinterest to
 * explain how refresh works on the API. Have a look at refresh_access_token
 * script if you need to refresh and to store an existing access token.
 * This script extends the example in get_access_token.py by demonstrating
 * how to use the OAuth refresh token to obtain a new access token.
 * It executes the refresh twice, verifying each time that the access token
 * has actually changed and that the new access token can be used to access
 * the associated user's profile.
 */
async function main(argv) {
  const parser = new ArgumentParser({ description: 'Get Pinterest OAuth token' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, { name: args.access_token });

  await access_token.fetch({ scopes: [Scope.READ_USERS], refreshable: true });
  let hashed = access_token.hashed();
  const access_token_hashes = new Set();
  access_token_hashes.add(hashed);
  console.log('hashed access token:', hashed);
  try {
    console.log('hashed refresh token:', access_token.hashed_refresh_token());
  } catch (err) {
    console.log(err);
    process.exit(2);
  }

  // use the access token to get information about the user
  const user = new User(api_config, access_token);
  let user_data = await user.get();
  user.print_summary(user_data);

  // refresh the access_token
  // Note that the AccessToken encapsulates the credentials,
  // so there is no need to refresh the User or other objects.
  await access_token.refresh({});
  hashed = access_token.hashed();
  if (access_token_hashes.has(hashed)) {
    console.log('Access Token is the same after refresh.');
    process.exit(2);
  }
  access_token_hashes.add(hashed);

  // This call demonstrates that the access_token has changed
  // without printing the actual token.
  console.log('hashed access token:', hashed);
  console.log('hashed refresh token:', access_token.hashed_refresh_token());

  console.log('accessing with refreshed access_token...');
  user_data = await user.get();
  user.print_summary(user_data);

  // Doing refreshes too quickly can result in the same access_token being generated.
  // In practice, this isn't a problem because tokens should be refreshed after
  // relatively long periods of time.
  console.log('wait a second to avoid getting the same token on the second refresh...');
  await new Promise(resolve => setTimeout(resolve, 1000));

  // refresh the access_token again
  await access_token.refresh({});

  // Verify that the access_token has changed again.
  hashed = access_token.hashed();
  console.log('hashed access token:', hashed);
  console.log('hashed refresh token:', access_token.hashed_refresh_token());
  if (access_token_hashes.has(hashed)) {
    console.log('Access Token is repeated after the second refresh.');
    process.exit(2);
  }
  console.log('accessing with second refreshed access_token...');
  user_data = await user.get();
  user.print_summary(user_data);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
