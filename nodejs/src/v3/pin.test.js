import {ApiObject} from '../api_object.js'
import {Pin} from './pin.js'

jest.mock('../api_object');

describe('v3 pin tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 pin methods', async () => {
    const test_pin = new Pin('test_pin_id', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    var response = await test_pin.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v3/pins/test_pin_id/');
    expect(response).toEqual('test_response');

    const pin_data = {
      link: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
      ignore: 'ignored',
      image_large_url: 'image_large_url_is_best_available'
    }

    // create pin without a section
    const mock_put_data = jest.spyOn(ApiObject.prototype, 'put_data');
    const created_data = {id: 'created_pin_id'};
    mock_put_data.mockResolvedValue(created_data);
    response = await test_pin.create(pin_data, 'test_board_id', {});
    expect(created_data).toEqual(response);
    const expected_put_data = {
      board_id: 'test_board_id',
      image_url: 'image_large_url_is_best_available',
      source_url: 'test_pin_link',
      title: 'My Test Pin',
      alt_text: 'This is what a test pin looks like',
    };
    expect(mock_put_data.mock.calls[0]).toEqual(['/v3/pins/', expected_put_data]);
    expect(test_pin.pin_id).toEqual('created_pin_id');

    // create pin in a section and without a link
    created_data.id = 'created_pin_id2';
    delete(pin_data.link);
    response = await test_pin.create(pin_data, 'test_board_id', {section: 'test_section_id'});
    const section_data = {name: 'New Section Name', ignore: 'ignored'};
    expect(created_data).toEqual(response);
    expected_put_data.section = 'test_section_id';
    delete(expected_put_data.source_url);
    expect(mock_put_data.mock.calls[1]).toEqual(['/v3/pins/', expected_put_data]);
  });
});

