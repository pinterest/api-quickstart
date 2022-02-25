import { ApiMediaObject } from '../api_media_object.js';
import { Pin } from './pin.js';

jest.mock('../api_media_object');
const amo_actual = jest.requireActual('../api_media_object');

describe('v3 pin tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 pin methods', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');
    expect(ApiMediaObject.mock.instances.length).toBe(1);
    expect(ApiMediaObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiMediaObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    let response = await test_pin.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v3/pins/test_pin_id/');
    expect(response).toEqual('test_response');

    const carousel_data = {
      carousel_slots: {
        details: 'string',
        id: 'string',
        images: {
          height: 450,
          url: 'string',
          width: 236
        },
        link: 'string',
        title: 'string'
      },
      id: 'number in a string',
      index: 'another number in a string'
    };

    const pin_data = {
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      ignore: 'ignored',
      carousel_data: carousel_data,
      image_large_url: 'image_large_url_is_best_available'
    };

    // create pin without a section
    const mock_put_data = jest.spyOn(ApiMediaObject.prototype, 'put_data');
    const created_data = { id: 'created_pin_id' };
    mock_put_data.mockResolvedValue(created_data);
    response = await test_pin.create(pin_data, 'test_board_id', {});
    expect(created_data).toEqual(response);
    const expected_put_data = {
      board_id: 'test_board_id',
      image_url: 'image_large_url_is_best_available',
      source_url: 'test_pin_link',
      title: 'My Test Pin',
      carousel_data_json: JSON.stringify(carousel_data),
      alt_text: 'This is what a test pin looks like'
    };
    expect(mock_put_data.mock.calls[0]).toEqual(['/v3/pins/', expected_put_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    // create pin in a section and without a link
    created_data.id = 'created_pin_id2';
    delete pin_data.link;
    response = await test_pin.create(pin_data, 'test_board_id', { section: 'test_section_id' });
    expect(created_data).toEqual(response);
    expected_put_data.section = 'test_section_id';
    delete expected_put_data.source_url;
    expect(mock_put_data.mock.calls[1]).toEqual(['/v3/pins/', expected_put_data]);
  });

  test('v3 create video pin', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');

    const mock_request_data = jest.spyOn(ApiMediaObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    mock_request_data // simulated responses to upload status
      // first call to create
      .mockResolvedValueOnce({
        test_media_id: { status: 'succeeded' }
      })
      // second call to create
      .mockResolvedValueOnce({
        12345: { status: 'failed' }
      })
      // third call to create
      .mockResolvedValueOnce({
        314159265: { status: 'failed', failure_code: 2718 }
      })
      // fourth call to create
      .mockResolvedValueOnce({
        oops_bad_media_id: { status: 'failed', failure_code: 2718 }
      })
      // fifth call to create
      .mockResolvedValueOnce({
        93428665: { 'not status': 'failed' }
      })
      // sixth call: seven responses
      .mockResolvedValueOnce({ 67890: { status: 'registered' } })
      .mockResolvedValueOnce({ 67890: { status: 'processing' } })
      .mockResolvedValueOnce({ 67890: { status: 'processing' } })
      .mockResolvedValueOnce({ 67890: { status: 'processing' } })
      .mockResolvedValueOnce({ 67890: { status: 'processing' } })
      .mockResolvedValueOnce({ 67890: { status: 'processing' } })
      .mockResolvedValueOnce({ 67890: { status: 'succeeded' } });

    const mock_m2mi = jest.spyOn(ApiMediaObject.prototype, 'media_to_media_id');
    mock_m2mi // simulated responses to media_to_media_id
      .mockResolvedValueOnce('test_media_id')
      .mockResolvedValueOnce('12345')
      .mockResolvedValueOnce('314159265')
      .mockResolvedValueOnce('314159265')
      .mockResolvedValueOnce('93428665')
      .mockResolvedValueOnce('67890');

    const pin_data = {
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      ignore: 'ignored',
      image_large_url: 'image_large_url_is_best_available'
    };

    // first call to create video pin
    const mock_put_data = jest.spyOn(ApiMediaObject.prototype, 'put_data');
    const created_data = { id: 'created_pin_id' };
    mock_put_data.mockResolvedValue(created_data);
    const response = await test_pin.create(pin_data, 'test_board_id', { media: 'test_media_id' });
    expect(created_data).toEqual(response);
    const expected_put_data = {
      board_id: 'test_board_id',
      image_url: 'image_large_url_is_best_available',
      source_url: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      media_upload_id: 'test_media_id'
    };
    expect(mock_put_data.mock.calls[0]).toEqual(['/v3/pins/', expected_put_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    await expect(async() => {
      // second call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('upload 12345 failed with code: unknown')
    );

    await expect(async() => {
      // third call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('upload 314159265 failed with code: 2718')
    );

    await expect(async() => {
      // fourth call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('upload 314159265 not found')
    );

    await expect(async() => {
      // fifth call to create
      await test_pin.create(pin_data, 'test_board_id', { media: 'file_name' });
    }).rejects.toThrowError(
      new Error('upload 93428665 has no status')
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

    // sixth call to create
    await test_pin.create(pin_data, 'test_board_id', { media: 'test_media_id' });

    // verify that the backoff algorithm is working as expected
    expect(timeout_calls).toEqual([
      1000, 2000, 4000, 8000, 10000, 10000
    ]);

    expect(console.log.mock.calls).toEqual([
      ['Upload 67890 status: registered. Waiting a second...'],
      ['Upload 67890 status: processing. Waiting 2 seconds...'],
      ['Upload 67890 status: processing. Waiting 4 seconds...'],
      ['Upload 67890 status: processing. Waiting 8 seconds...'],
      ['Upload 67890 status: processing. Waiting 10 seconds...'],
      ['Upload 67890 status: processing. Waiting 10 seconds...']
    ]);
  });

  test('v3 upload media', async() => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');

    const test_upload_parameters = { key1: 'value1', key2: 'value2' };

    const mock_post_data = jest.spyOn(ApiMediaObject.prototype, 'post_data');
    mock_post_data.mockResolvedValue({
      upload_id: 'test_media_id',
      upload_url: 'test_upload_url',
      upload_parameters: test_upload_parameters
    });

    const mock_upload_file_multipart = jest.spyOn(
      ApiMediaObject.prototype, 'upload_file_multipart'
    );

    const media_id = await test_pin.upload_media('test_media_path');
    expect(media_id).toEqual('test_media_id');
    expect(mock_post_data.mock.calls).toEqual([[
      '/v3/media/uploads/register/', { type: 'video' }
    ]]);
    expect(mock_upload_file_multipart.mock.calls).toEqual([[
      'test_upload_url', 'test_media_path', test_upload_parameters
    ]]);
  });
});
