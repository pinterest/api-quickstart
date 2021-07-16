import {ApiObject} from '../api_object.js'
import {Board} from './board.js'

export class User extends ApiObject {
  constructor(user, api_config, access_token) {
    super(api_config, access_token);
    this.user = user;
  }

  // https://developers.pinterest.com/docs/v5/#tag/user_accounts
  async get() {
    return await super.request_data('/v5/user_account');
  }

  async get_businesses() {
    console.log('Businesses endpoint is not available in v5.')
    return null
  }

  print_summary(user_data) {
    console.log('--- User Summary ---');
    console.log('Username:', user_data.username);
    console.log('Account Type:', user_data.account_type);
    console.log('Profile Image:',user_data.profile_image);
    console.log('Website URL:', user_data.website_url);
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/v5/#operation/boards/list
  async get_boards(user_data, {query_parameters}) {
    var path = '/v5/boards';
    if (query_parameters) {
      var delimiter = '?';
      for (const [query_parameter, value] of Object.entries(query_parameters)) {
        path += delimiter + query_parameter + '=' + value;
        delimiter = '&'
      }
    }
    return this.get_iterator(path); // iterator that handles API paging
  }

  // getting all of a user's pins is not supported, so iterate through boards
  async get_pins(user_data, {query_parameters}) {
    const user = this;
    const board_iterator = await this.get_boards(user_data,
                                                 {query_parameters: query_parameters});
    return {
      [Symbol.asyncIterator]: async function*() {
        for await (let board_data of board_iterator) {
          const board = new Board(board_data.id, user.api_config, user.access_token);
          const pin_iterator = await board.get_pins();
          for await (let pin_data of pin_iterator) {
            yield pin_data;
          }
        }
      }
    }
  }
}
