import { ApiMediaObject } from '../api_media_object.js';
import { Pin } from './pin.js';

jest.mock('../api_media_object');
const amo_actual = jest.requireActual('../api_media_object');

describe('v5 pin tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 pin methods', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');
    expect(ApiMediaObject.mock.instances.length).toBe(1);
    expect(ApiMediaObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiMediaObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    let response = await test_pin.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/pins/test_pin_id');
    expect(response).toEqual('test_response');

    const pin_data = {
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      ignore: 'ignored',
      media: { images: { originals: { url: 'test_pin_image_url' } } }
    };

    // create pin without a section
    const mock_post_data = jest.spyOn(ApiMediaObject.prototype, 'post_data');
    const created_data = { id: 'created_pin_id' };
    mock_post_data.mockResolvedValue(created_data);
    response = await test_pin.create(pin_data, 'test_board_id', {});
    expect(created_data).toEqual(response);
    const expected_post_data = {
      board_id: 'test_board_id',
      media_source: {
        source_type: 'image_url',
        url: 'test_pin_image_url'
      },
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like'
    };
    expect(mock_post_data.mock.calls[0]).toEqual(['/v5/pins', expected_post_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    // create pin in a section
    created_data.id = 'created_pin_id2';
    response = await test_pin.create(pin_data, 'test_board_id', { section: 'test_section_id' });
    expect(created_data).toEqual(response);
    expected_post_data.board_section_id = 'test_section_id';
    expect(mock_post_data.mock.calls[1]).toEqual(['/v5/pins', expected_post_data]);
  });

  test('v5 create video pin', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');

    const mock_request_data = jest.spyOn(ApiMediaObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    mock_request_data // simulated responses to upload status
      // first call to create
      .mockResolvedValueOnce({ status: 'succeeded' })
      // second call to create
      .mockResolvedValueOnce({ status: 'failed' })
      // third call to create
      .mockResolvedValueOnce({ 'oops no status': 'nothing to see here' })
      // fourth call to create
      .mockResolvedValueOnce({ status: 'registered' })
      .mockResolvedValueOnce({ status: 'processing' })
      .mockResolvedValueOnce({ status: 'processing' })
      .mockResolvedValueOnce({ status: 'processing' })
      .mockResolvedValueOnce({ status: 'processing' })
      .mockResolvedValueOnce({ status: 'processing' })
      .mockResolvedValueOnce({ status: 'succeeded' });

    const mock_m2mi = jest.spyOn(ApiMediaObject.prototype, 'media_to_media_id');
    mock_m2mi // simulated responses to media_to_media_id
      .mockResolvedValueOnce('test_media_id')
      .mockResolvedValueOnce('12345')
      .mockResolvedValueOnce('314159265')
      .mockResolvedValueOnce('67890');

    const pin_data = {
      alt_text: 'This is what a test pin looks like',
      description: 'test description',
      link: 'test_pin_link',
      media: { images: { originals: { url: 'test_image_url' } } }
    };

    // first call to create video pin
    const mock_post_data = jest.spyOn(ApiMediaObject.prototype, 'post_data');
    const created_data = { id: 'created_pin_id' };
    mock_post_data.mockResolvedValue(created_data);
    const response = await test_pin.create(pin_data, 'test_board_id', { media: 'test_media_id' });
    expect(created_data).toEqual(response);
    const expected_post_data = {
      board_id: 'test_board_id',
      media_source: {
        source_type: 'video_id',
        cover_image_url: 'test_image_url',
        media_id: 'test_media_id'
      },
      link: 'test_pin_link',
      alt_text: 'This is what a test pin looks like',
      description: 'test description'
    };
    expect(mock_request_data.mock.calls).toEqual([[
      '/v5/media/test_media_id'
    ]]);
    expect(mock_post_data.mock.calls[0]).toEqual(['/v5/pins', expected_post_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    await expect(async() => {
      // second call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('media upload 12345 failed')
    );

    await expect(async() => {
      // third call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('media upload 314159265 not found')
    );

    console.log = jest.fn(); // test output

    // Return from setTimeout immediately, saving the requested timeout.
    // Note: jest.useFakeTimers() is hard to use with async functions,
    //       so this test uses a more basic approach.
    const mock_set_timeout = jest.spyOn(global, 'setTimeout');
    const timeout_calls = [];
    mock_set_timeout.mockImplementation((callback, timeout) => {
      timeout_calls.push(timeout); // save the requested timeout
      callback(); // run the timer callback immediately
    });

    // unmock the backoff functions
    const api_media_object = new amo_actual.ApiMediaObject('test1', 'test2');
    jest.spyOn(ApiMediaObject.prototype, 'reset_backoff')
      .mockImplementation(api_media_object.reset_backoff);
    jest.spyOn(ApiMediaObject.prototype, 'wait_backoff')
      .mockImplementation(api_media_object.wait_backoff);

    // fourth call to create
    await test_pin.create(pin_data, 'test_board_id', { media: 'test_media_id' });

    // verify that the backoff algorithm is working as expected
    expect(timeout_calls).toEqual([
      1000, 2000, 4000, 8000, 10000, 10000
    ]);

    expect(console.log.mock.calls).toEqual([
      ['Media id 67890 status: registered. Waiting a second...'],
      ['Media id 67890 status: processing. Waiting 2 seconds...'],
      ['Media id 67890 status: processing. Waiting 4 seconds...'],
      ['Media id 67890 status: processing. Waiting 8 seconds...'],
      ['Media id 67890 status: processing. Waiting 10 seconds...'],
      ['Media id 67890 status: processing. Waiting 10 seconds...']
    ]);
  });

  test('v5 upload media', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');

    const test_upload_parameters = { key1: 'value1', key2: 'value2' };

    const mock_post_data = jest.spyOn(ApiMediaObject.prototype, 'post_data');
    mock_post_data.mockResolvedValue({
      media_id: 'test_media_id',
      upload_url: 'test_upload_url',
      upload_parameters: test_upload_parameters
    });

    const mock_upload_file_multipart = jest.spyOn(
      ApiMediaObject.prototype, 'upload_file_multipart'
    );

    const media_id = await test_pin.upload_media('test_media_path');
    expect(media_id).toEqual('test_media_id');
    expect(mock_post_data.mock.calls).toEqual([[
      '/v5/media', { media_type: 'video' }
    ]]);
    expect(mock_upload_file_multipart.mock.calls).toEqual([[
      'test_upload_url', 'test_media_path', test_upload_parameters
    ]]);
  });
});
