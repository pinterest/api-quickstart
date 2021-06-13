import {ApiObject} from './api_object.js'

export class Board extends ApiObject {
  constructor(board_id, api_config, access_token) {
    super(api_config, access_token);
    this.board_id= board_id;
  }

  static print_summary(board_data) {
    console.log('--- Board Summary ---');
    console.log('Board ID:', board_data.id);
    console.log('Name:', board_data.name);
    console.log('URL:', board_data.url);
    console.log('Category:', board_data.category);
    console.log('Description:', board_data.description);
    console.log('Pin Count:', board_data.pin_count);
    console.log('--------------------');
  }
}
