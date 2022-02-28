import { ApiMediaObject } from './api_media_object.js';
import fs from 'fs';

jest.mock('fs');

const mockFormAppend = jest.fn();
const mockFormSubmit = jest.fn();
jest.mock('form-data', () => {
  return jest.fn().mockImplementation(() => {
    return {
      append: mockFormAppend,
      submit: mockFormSubmit
    };
  });
});

/*
 * Tests for the generic ApiObject class that is used for all versions
 * of the Pinterest API.
 *
 * Note: the reset_backoff and wait_backoff functions are tested with
 * the classes that call these functions instead of testing them in
 * this file.
 */
describe('api_media_object tests', () => {
  test('upload_media', async() => {
    const api_media_object = new ApiMediaObject(jest.fn(), jest.fn());

    await expect(async() => {
      await api_media_object.upload_media('test_media');
    }).rejects.toThrowError(new Error('upload_media() must be overridden'));
  });

  test('media_to_media_id', async() => {
    const api_media_object = new ApiMediaObject(jest.fn(), jest.fn());

    // falsy returns falsy
    expect(await api_media_object.media_to_media_id(null))
      .toBeNull();

    await expect(async() => {
      await api_media_object.upload_media('test_media');
    }).rejects.toThrowError(new Error('upload_media() must be overridden'));

    // media id returns media id
    fs.openSync
      .mockImplementationOnce(
        (path, mode) => { throw new Error('file does not exist'); });
    expect(await api_media_object.media_to_media_id('12345'))
      .toEqual('12345');

    // valid file calls closeSync and upload_media
    fs.openSync.mockReturnValueOnce('test_media_fd');
    await expect(async() => {
      await api_media_object.media_to_media_id('test_media');
    }).rejects.toThrowError(new Error('upload_media() must be overridden'));
    expect(fs.closeSync.mock.calls).toEqual([['test_media_fd']]);

    // invalid media throws error
    fs.openSync
      .mockImplementationOnce(
        (path, mode) => { throw new Error('file does not exist'); })
      .mockImplementationOnce(
        (path, mode) => { throw new Error('file does not exist'); });

    await expect(async() => {
      await api_media_object.media_to_media_id('3.14159');
    }).rejects.toThrowError(new Error('invalid media: 3.14159'));

    await expect(async() => {
      await api_media_object.media_to_media_id('-314159');
    }).rejects.toThrowError(new Error('invalid media: -314159'));
  });

  test('upload_file_multipart', async() => {
    const api_config = jest.fn();
    api_config.credentials_warning = jest.fn();
    const api_media_object = new ApiMediaObject(api_config, jest.fn());

    console.log = jest.fn(); // test output

    fs.createReadStream
      .mockReturnValueOnce('video_stream_1')
      .mockReturnValueOnce('video_stream_2');
    const post_data = {
      key1: 'value1',
      key2: 'value2'
    };

    const submitError = new Error('something went wrong');
    mockFormSubmit
      .mockReturnValueOnce('return_1') // success first
      .mockImplementationOnce((url, callback) => {
        callback(submitError, null); // error second
      });

    api_config.verbosity = 3; // print everything
    await api_media_object.upload_file_multipart(
      'test_url_1', 'test_file_path_1', post_data);

    api_config.verbosity = 1; // print nothing
    await expect(async() => {
      await api_media_object.upload_file_multipart(
        'test_url_2', 'test_file_path_2', null);
    }).rejects.toThrowError(submitError);

    expect(fs.createReadStream.mock.calls).toEqual([
      ['test_file_path_1'],
      ['test_file_path_2']
    ]);
    expect(api_config.credentials_warning).toHaveBeenCalledTimes(1);
    expect(mockFormAppend.mock.calls).toEqual([
      ['key1', 'value1'],
      ['key2', 'value2'],
      ['file', 'video_stream_1'],
      ['file', 'video_stream_2']
    ]);
    expect(mockFormSubmit.mock.calls).toEqual([
      ['test_url_1', expect.any(Function)],
      ['test_url_2', expect.any(Function)]
    ]);
    expect(console.log.mock.calls).toEqual([
      ['POST', 'test_url_1', 'from', 'test_file_path_1'],
      [post_data]
    ]);
  });
});
