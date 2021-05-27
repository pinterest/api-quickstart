#!/usr/bin/env node
import {ArgumentParser} from 'argparse'

import {AccessToken} from '../src/access_token.js'
import {ApiConfig} from '../src/api_config.js'
import {Scope} from '../src/oauth_scope.js'

async function main (argv) {
  const parser = new ArgumentParser({
    description: 'Get Pinterest OAuth token'
  });
  parser.add_argument('-w', '--write', {action:'store_true', help:'write access token to file'});
  parser.add_argument('-ct', '--cleartext', {action:'store_true', help:'print the token in clear text'});
  parser.add_argument('-s', '--scopes', {help:'comma separated list of scopes'});
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();
  api_config.verbosity = 2;

  // imports that depend on the version of the API
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {});
  await access_token.fetch({});

  // Note: It is best practice not to print credentials in clear text.
  // Pinterest engineers asked for this capability to make it easier to support partners.
  if (args.cleartext) {
    console.warn('Please keep clear text tokens secure!')
    console.log('clear text access token: ' + access_token.access_token)
  }
  console.log('hashed access token:', access_token.hashed());

  if (access_token.refresh_token) {
    if (args.cleartext) {
      console.log('clear text refresh token: ' + access_token.refresh_token);
    }
    console.log('hashed refresh token:', access_token.hashed_refresh_token());
  }

  // Save the token, if requested. The comment at the top of this script provides more
  // information about this feature.
  if (args.write) {
    console.log('writing access token');
    access_token.write();
  }

  // use the access token to get information about the user
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
