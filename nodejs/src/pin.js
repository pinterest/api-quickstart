import { ApiMediaObject } from './api_media_object.js';

export class Pin extends ApiMediaObject {
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
    console.log('Title:', pin_data.title);
    console.log('Description:', pin_data.description);
    console.log('Link:', pin_data.link);
    console.log('Domain:', pin_data.domain);
    console.log('Section ID:', pin_data.board_section_id);
    console.log('--------------------');
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/pins/save
  async save(board_id, { section }) {
    if (!this.pin_id) {
      throw new Error('pin_id must be set to save a pin');
    }
    const save_data = { board_id: board_id };
    if (section) {
      save_data.board_section_id = section;
    }
    return this.post_data(`/v5/pins/${this.pin_id}/save`, save_data);
  }

  max_resolution_image_url(pin_data) {
    let max_res = 0; // maximum resolution of either dimension
    let url = null; // url for the max resolution image

    for (const image of Object.values(pin_data.media.images)) {
      if (image.width > max_res) {
        max_res = image.width;
        url = image.url;
      }
      if (image.height > max_res) {
        max_res = image.height;
        url = image.url;
      }
    }
    return url;
  }

  // https://developers.pinterest.com/docs/api/v5/#operation/pins/create
  async create(pin_data, board_id, { section, media }) {
    const OPTIONAL_ATTRIBUTES = [
      'link',
      'title',
      'description',
      'alt_text'
    ];
    const create_data = {
      board_id: board_id
    };

    // https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
    const media_id = await this.media_to_media_id(media);

    const image_url = this.max_resolution_image_url(pin_data);
    if (media_id) {
      await this.check_media_id(media_id);
      create_data.media_source = {
        source_type: 'video_id',
        cover_image_url: image_url,
        media_id: media_id
      };
    } else {
      create_data.media_source = {
        source_type: 'image_url',
        url: image_url
      };
    }

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

  // Upload a video from the specified path and return a media_id.
  // Called by ApiMediaObject:media_to_media_id().
  // https://developers.pinterest.com/docs/api/v5/#operation/media/create
  async upload_media(media_path) {
    const media_upload = await this.post_data('/v5/media', {
      media_type: 'video'
    });

    // upload the video file
    await this.upload_file_multipart(media_upload.upload_url,
      media_path,
      media_upload.upload_parameters);
    return media_upload.media_id;
  }

  // Poll for the status of the media until it is complete.
  // https://developers.pinterest.com/docs/api/v5/#operation/media/get
  async check_media_id(media_id) {
    this.reset_backoff();
    while (true) {
      const media_response = await this.request_data(`/v5/media/${media_id}`);
      const status = media_response.status;
      if (!status) {
        throw Error(`media upload ${media_id} not found`);
      }
      if (status === 'succeeded') {
        return;
      }
      if (status === 'failed') {
        throw Error(`media upload ${media_id} failed`);
      }
      await this.wait_backoff({
        message: `Media id ${media_id} status: ${status}.`
      });
    }
  }
}
