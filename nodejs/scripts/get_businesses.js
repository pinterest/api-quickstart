import AccessToken from '../src/access_token.js'
import ApiConfig from '../src/api_config.js'
import Scope from '../src/oauth_scope.js'
import User from '../src/user.js'

async function main () {
  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig();

  // Note that the OAuth will fail if your application does not
  // have access to the scope that is required to access
  // linked business accounts.
  const access_token = new AccessToken(api_config, {
    scopes: [Scope.READ_USERS, Scope.READ_ADVERTISERS],
    refreshable: true
  });
  await access_token.oauth();

  // use the access token to get information about the user
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  console.log('trying /v3/users/me/businesses...')
  const user_me_businesses = await user_me.get_businesses();
  if (user_me_businesses && (user_me_businesses.length != 0)) {
    console.log(user_me_businesses);
  } else {
    console.log('This account has no information on linked businesses.');
  }
}

if (!process.env.TEST_ENV) {
  main();
}
