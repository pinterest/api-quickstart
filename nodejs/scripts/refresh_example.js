#!/usr/bin/env node
import {AccessToken} from '../src/access_token.js'
import {ApiConfig} from '../src/api_config.js'
import {Scope} from '../src/oauth_scope.js'

async function main () {
  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();

  // imports that depend on the version of the API
  const {User} = await import(`../src/${api_config.version}/user.js`);

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, {});

  await access_token.fetch({scopes: [Scope.READ_USERS],refreshable:true});
  var hashed = access_token.hashed();
  var access_token_hashes = new Set();
  access_token_hashes.add(hashed);
  console.log('hashed access token:', hashed);
  try {
    console.log('hashed refresh token:', access_token.hashed_refresh_token());
  } catch (err) {
    console.log(err);
    process.exit(2);
  }

  // use the access token to get information about the user
  const user_me = new User('me', api_config, access_token);
  var user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  // refresh the access_token
  // Note that the AccessToken encapsulates the credentials,
  // so there is no need to refresh the User or other objects.
  await access_token.refresh();
  hashed = access_token.hashed();
  if (access_token_hashes.has(hashed)) {
    throw 'Access Token is the same after refresh.'
  }
  access_token_hashes.add(hashed);

  // This call demonstrates that the access_token has changed
  // without printing the actual token.
  console.log('hashed access token:', hashed);

  console.log('accessing with refreshed access_token...');
  user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  // Doing refreshes too quickly can result in the same access_token being generated.
  // In practice, this isn't a problem because tokens should be refreshed after
  // relatively long periods of time.
  console.log('wait a second to avoid getting the same token on the second refresh...')
  await new Promise(resolve => setTimeout(resolve, 1000));

  // refresh the access_token again
  await access_token.refresh();

  // Verify that the access_token has changed again.
  hashed = access_token.hashed();
  if (access_token_hashes.has(hashed)) {
    throw 'Access Token is repeated after the second refresh.'
  }
  console.log('hashed access token:', hashed);

  console.log('accessing with second refreshed access_token...');
  user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);
}

if (!process.env.TEST_ENV) {
  main();
}
