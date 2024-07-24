import { ApiObject } from './api_object.js';

export class User extends ApiObject {
  // https://developers.pinterest.com/docs/api/v5/user_account-get/
  async get() {
    return await super.request_data('/v5/user_account');
  }

  print_summary(user_data) {
    console.log('--- User Summary ---');
    console.log('Username:', user_data.username);
    console.log('Account Type:', user_data.account_type);
    console.log('Profile Image:', user_data.profile_image);
    console.log('Website URL:', user_data.website_url);
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/api/v5/boards-list/
  async get_boards(query_parameters = {}) {
    // iterator that handles API paging
    return this.get_iterator('/v5/boards', query_parameters);
  }

  // https://developers.pinterest.com/docs/api/v5/pins-list/
  async get_pins(query_parameters = {}) {
    return this.get_iterator('/v5/pins', query_parameters);
  }
}
