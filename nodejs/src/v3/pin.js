import { ApiMediaObject } from '../api_media_object.js';

export class Pin extends ApiMediaObject {
  constructor(pin_id, api_config, access_token) {
    super(api_config, access_token);
    this.pin_id = pin_id;
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_get_pin_GET
  async get() {
    if (!this.pin_id) {
      throw new Error('pin_id must be set to get a pin');
    }
    return this.request_data(`/v3/pins/${this.pin_id}/`);
  }

  static print_summary(pin_data) {
    console.log('--- Pin Summary ---');
    console.log(`Pin ID: ${pin_data.id}`);
    console.log(`Type: ${pin_data.type}`);
    if (!pin_data.type || pin_data.type === 'pin') {
      console.log(`Description: ${pin_data.description}`);
      console.log(`Domain: ${pin_data.domain}`);
      console.log(`Native format type: ${pin_data.native_format_type}`);
    } else if (pin_data.type === 'story') {
      console.log(`Story type: ${pin_data.story_type}`);
    }
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_partner_save_handler_POST
  // This method is only for the sake of completeness. In general, it's better to use
  // API version 5. In the v3 API, this endpoint is limited to certain kinds of partners
  // (e.g. the "pinner_app" category).
  async save(board_id, { section }) {
    if (!this.pin_id) {
      throw new Error('pin_id must be set to save a pin');
    }
    const save_data = { board_id: board_id };
    if (section) {
      save_data.board_section_id = section;
    }
    return this.post_data(`/v3/partners/pins/${this.pin_id}/save/`, save_data);
  }

  // https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT
  async create(pin_data, board_id, { section, media }) {
    const OPTIONAL_ATTRIBUTES = [
      'alt_text',
      'description',
      'title'
    ];
    const create_data = {
      board_id: board_id,
      image_url: pin_data.image_large_url
    };

    // https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
    const media_id = await this.media_to_media_id(media);
    if (media_id) {
      await this.check_upload_id(media_id);
      create_data.media_upload_id = media_id;
    }

    if (section) {
      create_data.section = section;
    }
    const link = pin_data.link;
    if (link) {
      create_data.source_url = link;
    }
    const carousel_data = pin_data.carousel_data;
    if (carousel_data) {
      create_data.carousel_data_json = JSON.stringify(pin_data.carousel_data);
    }

    for (const key of OPTIONAL_ATTRIBUTES) {
      const value = pin_data[key];
      if (value) {
        create_data[key] = value;
      }
    }

    const new_pin_data = await this.put_data('/v3/pins/', create_data);
    this.pin_id = new_pin_data.id;
    return new_pin_data;
  }

  // Upload a video from the specified path and return a media_id.
  // Called by ApiMediaObject:media_to_media_id().
  // https://developers.pinterest.com/docs/redoc/#operation/register_media_upload_POST
  async upload_media(media_path) {
    const media_upload = await this.post_data(
      '/v3/media/uploads/register/',
      { type: 'video' }
    );

    // upload the video file
    await this.upload_file_multipart(media_upload.upload_url,
      media_path,
      media_upload.upload_parameters);
    return media_upload.upload_id;
  }

  // Poll for the status of the media until it is complete.
  // https://developers.pinterest.com/docs/redoc/#operation/get_media_uploads_GET
  async check_upload_id(upload_id) {
    this.reset_backoff();
    while (true) {
      const media_response = await this.request_data(
        `/v3/media/uploads/?upload_ids=${upload_id}`
      );
      const upload_record = media_response[upload_id];
      if (!upload_record) {
        throw Error(`upload ${upload_id} not found`);
      }
      const status = upload_record.status;
      if (!status) {
        throw Error(`upload ${upload_id} has no status`);
      }
      if (status === 'succeeded') {
        return;
      }
      if (status === 'failed') {
        const failure_code = upload_record.failure_code || 'unknown';
        throw Error(`upload ${upload_id} failed with code: ${failure_code}`);
      }
      await this.wait_backoff({
        message: `Upload ${upload_id} status: ${status}.`
      });
    }
  }
}
