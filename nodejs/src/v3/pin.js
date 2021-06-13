import {ApiObject} from './api_object.js'

export class Pin extends ApiObject {
  constructor(pin_id, api_config, access_token) {
    super(api_config, access_token);
    this.pin_id= pin_id;
  }

  static print_summary(pin_data) {
    console.log('--- Pin Summary ---');
    console.log(`Pin ID: ${pin_data.id}`);
    console.log(`Type: ${pin_data.type}`);
    if (pin_data.type == 'pin') {
      console.log(`Description: ${pin_data.description}`);
      console.log(`Domain: ${pin_data.domain}`);
      console.log(`Native format type: ${pin_data.native_format_type}`);
    } else if (pin_data.type == 'story') {
      console.log(`Story type: ${pin_data.story_type}`);
    }
    console.log('--------------------');
  }
}
