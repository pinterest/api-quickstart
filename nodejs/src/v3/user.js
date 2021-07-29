import { ApiObject } from '../api_object.js';

export class User extends ApiObject {
  constructor(user, api_config, access_token) {
    super(api_config, access_token);
    this.user = user;
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_get_user_handler_GET
  async get() {
    return await super.request_data(`/v3/users/${this.user}/`);
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_get_linked_business_accounts_GET
  async get_businesses() {
    return await super.request_data(`/v3/users/${this.user}/businesses/`);
  }

  print_summary(user_data) {
    console.log('--- User Summary ---');
    console.log('Username:', user_data.username);
    console.log('Full Name:', user_data.full_name);
    console.log('About:', user_data.about);
    console.log('Profile URL:', user_data.profile_url);
    console.log('Pin Count:', user_data.pin_count);
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET
  async get_boards(user_data, { query_parameters }) {
    let path = `/v3/users/${user_data.id}/boards/feed/`;
    if (query_parameters) {
      let delimiter = '?';
      for (const [query_parameter, value] of Object.entries(query_parameters)) {
        path += delimiter + query_parameter + '=' + value;
        delimiter = '&';
      }
    }
    return this.get_iterator(path); // iterator that handles API paging
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_get_pins_handler_GET
  async get_pins(user_data, { query_parameters }) {
    let path = `/v3/users/${user_data.id}/pins/`;
    if (query_parameters) {
      let delimiter = '?';
      for (const [query_parameter, value] of Object.entries(query_parameters)) {
        path += delimiter + query_parameter + '=' + value;
        delimiter = '&';
      }
    }
    return this.get_iterator(path); // iterator that handles API paging
  }
}
