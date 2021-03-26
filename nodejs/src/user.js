import ApiObject from './api_object.js'

export default class User extends ApiObject {
  constructor(user, api_config, access_token) {
    super(api_config, access_token);
    this.user = user;
  }

  async get() {
    return await super.request_data(`/v3/users/${this.user}/`);
  }

  async get_businesses() {
    return await super.request_data(`/v3/users/${this.user}/businesses/`);
  }

  print_summary(user_data) {
    console.log('--- User Summary ---');
    console.log('Full Name:', user_data.full_name);
    console.log('About:', user_data.about);
    console.log('Profile URL:', user_data.profile_url);
    console.log('Pin Count: ' + user_data.pin_count);
    console.log('--------------------');
  }
}
