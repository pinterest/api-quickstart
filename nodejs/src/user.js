import { ApiObject } from './api_object.js';

export class User extends ApiObject {
  // https://developers.pinterest.com/docs/api/v5/#tag/user_account
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

  // https://developers.pinterest.com/docs/api/v5/#operation/boards/list
  async get_boards(user_data, query_parameters = {}) {
    // iterator that handles API paging
    return this.get_iterator('/v5/boards', query_parameters);
  }

  // getting all of a user's pins is not supported, so iterate through boards
  async get_pins(user_data, query_parameters = {}) {
    return this.get_iterator('/v5/pins', query_parameters);
  }
}
