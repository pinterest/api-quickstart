import FormData from 'form-data';
import { openSync, closeSync, createReadStream } from 'fs';
import { ApiObject } from './api_object.js';

/**
 * Subclass of an ApiObject with media functionality.
 */
export class ApiMediaObject extends ApiObject {
  constructor(api_config, access_token) {
    super(api_config, access_token);
  }

  // The implementation of this function depends on the API version,
  // so it must be overridden in the subclass for each version of the API.
  async upload_media(self, media) {
    throw new Error ('upload_media() must be overridden');
  }

  /*
   * This function translates the media argument into a media_id,
   * which may be one of:
   *   <falsy>     => no video creation is required
   *   <file path> => create a media_id from the video in the file path
   *   media_id    => an existing media identifier
   *
   * References:
   *   v3: https://developers.pinterest.com/docs/redoc/#section/Using-video-APIs
   *   v5: https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
   */
  async media_to_media_id(media) {
    if (!media) {
      return media;
    }

    try {
      let fd = openSync(media, 'r');
      closeSync(fd);
      return await this.upload_media(media); // TODO: remove await because caller will await return value?
    } catch {
      // ignore errors, check for media id
    }

    // verify that media_id is a positive integer
    let media_id = Number(media);
    if (Number.isInteger(media_id) && media_id > 0) {
      return media;
    }

    // otherwise, can not interpret media
    throw new Error(`invalid media: ${media}`);
  }

  // Upload a file in a form. For example, use this function
  // for uploading a file to Amazon S3 with the parameters
  // returned from the Pinterest media API.
   async upload_file_multipart(url, file_path, post_data) {
     if (this.api_config.verbosity >= 2) {
       console.log('POST', url, 'from', file_path);
     }

     if (this.api_config.verbosity >= 3) {
       this.api_config.credentials_warning();
       console.log(post_data);
     }

     // set up the form to be submitted with the video
     let form = new FormData();
     if (post_data) {
       for (const [attr, value] of Object.entries(post_data)) {
         form.append(attr, value);
       }
     }
     form.append('file', createReadStream(file_path));

     // submit the form with the video
     form.submit(url, function(err, res) {
       if (err) throw err;
     });
  }
}
