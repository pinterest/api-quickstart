import {ApiObject} from './api_object.js'

export class Pin extends ApiObject {
  constructor(pin_id, api_config, access_token) {
    super(api_config, access_token);
    this.pin_id= pin_id;
  }

  async get() {
    if (!this.pin_id) {
      throw 'pin_id must be set to get a pin';
    }
    return this.request_data(`/v3/pins/${this.pin_id}/`);
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

  async create(pin_data, board_id, {section=null}) {
    // TODO: carousel_data_json
    const OPTIONAL_ATTRIBUTES = [
      'alt_text',
      'description',
      'title',
    ];
    const create_data = {
      'board_id': board_id,
      'image_url': pin_data['image_large_url']
    };
    if (section) {
      create_data['section'] = section;
    }
    const link = pin_data.link;
    if (link) {
      create_data['source_url'] = link;
    }

    for (const key in OPTIONAL_ATTRIBUTES) {
      const value = pin_data[key];
      if (value) {
        create_data[key] = value;
      }
    }

    const new_pin_data = await this.put_data('/v3/pins/', create_data);
    this.pin_id = new_pin_data.id;
    return new_pin_data;
  }
}
