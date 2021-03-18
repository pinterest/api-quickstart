import AccessToken from '../src/access_token.js'
import ApiConfig from '../src/api_config.js'
import User from '../src/user.js'

const api_config = new ApiConfig();
const access_token = await new AccessToken(api_config, {
  scopes: ['read_users'],
  refreshable: true
});
await access_token.oauth();
console.log('hashed access token: ' + access_token.hashed());

const user_me = new User('me', api_config, access_token);
const user_me_data = await user_me.get();
user_me.print_summary(user_me_data);
