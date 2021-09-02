import { ApiObject } from '../api_object.js';

export class Pin extends ApiObject {
  constructor(pin_id, api_config, access_token) {
    super(api_config, access_token);
    this.pin_id = pin_id;
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/pins/get
  async get() {
    if (!this.pin_id) {
      throw new Error('pin_id must be set to get a pin');
    }
    return this.request_data(`/v5/pins/${this.pin_id}`);
  }

  static print_summary(pin_data) {
    console.log('--- Pin Summary ---');
    console.log('Pin ID:', pin_data.id);
    console.log('Description:', pin_data.description);
    console.log('Link:', pin_data.link);
    console.log('Domain:', pin_data.domain);
    console.log('Section ID:', pin_data.board_section_id);
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/pins/create
  async create(pin_data, board_id, { section }) {
    const OPTIONAL_ATTRIBUTES = [
      'link',
      'title',
      'description',
      'alt_text'
    ];
    const create_data = {
      board_id: board_id,
      media_source: {
        source_type: 'image_url',
        url: pin_data.media.images.originals.url
      }
    };
    if (section) {
      create_data.board_section_id = section;
    }

    for (const key of OPTIONAL_ATTRIBUTES) {
      const value = pin_data[key];
      if (value) {
        create_data[key] = value;
      }
    }

    const new_pin_data = await this.post_data('/v5/pins', create_data);
    this.pin_id = new_pin_data.id;
    return new_pin_data;
  }
}
