#!/usr/bin/env node
import {ArgumentParser} from 'argparse'

import {ApiConfig} from '../src/api_config.js'
import {common_arguments} from '../src/arguments.js'

/**
 * The arguments for this script are intended to be used as follows:
 *  -w / --write :
 *    Save the access token to a file in JSON format so that it can be used with other scripts.
 *    The name of the file is based on the 'name' attribute of the AccessToken object, which defaults to access_token,
 *    so the default file name is access_token.json. The directory used to store the file is in the
 *    PINTEREST_OAUTH_TOKEN_DIR environment variable, which is set to ../../common/oauth_tokens/ by
 *    the api_env script described in the top-level README for this repo. The access_token.json
 *    file written by this script may be renamed so that it is available for future use. For example,
 *    renaming access_token.json to my_account_token.json could then be retrieved by calling:
 *      AccessToken(api_config, name='my_account_token').fetch()
 *  -ct / --cleartext :
 *    It is best practice not to print credentials like access tokens and refresh tokens in clear text,
 *    so this script prints SHA256 hashes of tokens so that developers can check whether token values
 *    have changed. However, engineers at Pinterest requested the capability to print tokens in clear text,
 *    which is implemented using this argument.
 *  -s / --scopes :
 *    To provide a quick start for new developers, this script requests an access token with the default
 *    set of scopes for the application provided in the environment (with the PINTEREST_APP_ID and
 *    PINTEREST_APP_SECRET variables). This argument, which requires a comma-separated list of valid
 *    OAuth scopes, allows experimentation with different sets of scopes. Specifying scopes prevents
 *    the access token from being read from the environment or file system, and forces the use of
 *    the browser-based OAuth process.
 */
async function main (argv) {
  const parser = new ArgumentParser({description: 'Get Pinterest OAuth token'});
  parser.add_argument('-w', '--write', {action:'store_true', help:'write access token to file'});
  parser.add_argument('-ct', '--cleartext', {action:'store_true', help:'print the token in clear text'});
  parser.add_argument('-s', '--scopes', {help:'comma separated list of scopes'});
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({verbosity: args.log_level, version: args.api_version});

  // imports that depend on the version of the API
  const {AccessToken} = await import(`../src/${api_config.version}/access_token.js`);
  const {User} = await import(`../src/${api_config.version}/user.js`);
  const {Scope} = await import(`../src/${api_config.version}/oauth_scope.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {name: args.access_token});
  if (args.scopes) {
    // use the comma-separated list of scopes passed as a command-line argument
    const scopes = args.scopes.split(',').map(scopeArg => {
      const scope = Scope[scopeArg.toUpperCase()];
      if (scope) {
        return scope;
      }
      console.log('invalid scope:', scopeArg);
      parser.print_usage();
      process.exit(1);
    });
    await access_token.oauth({scopes:scopes});
  } else {
    // Try the different methods for getting an access token: from the environment,
    // from a file, and from Pinterest via the browser.
    try {
      await access_token.fetch({});
    } catch (error) { // probably because scopes are required
      console.log(error);
      parser.print_usage();
      process.exit(1);
    }
  }

  // Note: It is best practice not to print credentials in clear text.
  // Pinterest engineers asked for this capability to make it easier to support partners.
  if (args.cleartext) {
    console.warn('Please keep clear text tokens secure!');
    console.log('clear text access token:', access_token.access_token);
  }
  console.log('hashed access token:', access_token.hashed());

  if (access_token.refresh_token) {
    if (args.cleartext) {
      console.log('clear text refresh token:', access_token.refresh_token);
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
