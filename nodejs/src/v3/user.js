import {ApiObject} from './api_object.js'

export class User extends ApiObject {
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

  // documentation: https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET
  async get_boards(user_data, {query_parameters=null}) {
    var path = `/v3/users/${user_data.id}/boards/feed/`;
    if (query_parameters) {
      var delimiter = '?';
      for (const [query_parameter, value] of Object.entries(query_parameters)) {
        path += delimiter + query_parameter + '=' + value;
        delimiter = '&'
      }
    }
    return this.get_iterator(path); // iterator that handles API paging
  }

  async get_pins(user_data, {query_parameters=null}) {
    var path = `/v3/users/${user_data.id}/pins/`;
    if (query_parameters) {
      var delimiter = '?';
      for (const [query_parameter, value] of Object.entries(query_parameters)) {
        path += delimiter + query_parameter + '=' + value;
        delimiter = '&'
      }
    }
    return this.get_iterator(path); // iterator that handles API paging
  }
}
