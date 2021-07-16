import {ApiObject} from '../api_object.js'
import {Pin} from './pin.js'

jest.mock('../api_object');

describe('v5 pin tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 pin methods', async () => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    var response = await test_pin.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/pins/test_pin_id');
    expect(response).toEqual('test_response');

    const pin_data = {
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      ignore: 'ignored',
      media: {images: {originals: {url: 'test_pin_image_url'}}}
    }

    // create pin without a section
    const mock_post_data = jest.spyOn(ApiObject.prototype, 'post_data');
    const created_data = {id: 'created_pin_id'};
    mock_post_data.mockResolvedValue(created_data);
    response = await test_pin.create(pin_data, 'test_board_id', {});
    expect(created_data).toEqual(response);
    const expected_post_data = {
      board_id: 'test_board_id',
      media_source: {source_type: 'image_url',
                       url: 'test_pin_image_url'},
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
    };
    expect(mock_post_data.mock.calls[0]).toEqual(['/v5/pins', expected_post_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    // create pin in a section
    created_data.id = 'created_pin_id2';
    response = await test_pin.create(pin_data, 'test_board_id', {section: 'test_section_id'});
    const section_data = {name: 'New Section Name', ignore: 'ignored'};
    expect(created_data).toEqual(response);
    expected_post_data.board_section_id = 'test_section_id';
    expect(mock_post_data.mock.calls[1]).toEqual(['/v5/pins', expected_post_data]);
  });
});

