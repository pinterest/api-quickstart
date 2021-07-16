import {ApiObject} from '../api_object.js'
import {User} from './user.js'

jest.mock('../api_object');

describe('v3 user tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 user get', async () => {
    const test_user = new User('test_user', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    // Mocking the response from request_data in the instantiated copy of ApiObject
    // does not work, because User is a subclass of (extends) ApiObject. This would
    // work if User contained an ApiObject. (Had a "Has-A relationship" with ApiObject
    // instead of being a subclass.
    // const mock_request_data = ApiObject.mock.instances[0].request_data;

    // Instead of using the mock in the instance, need to use spyOn because User is a
    // subclass (extends) ApiObject.
    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data')
    mock_request_data.mockResolvedValueOnce('test_response');

    const response = await test_user.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v3/users/test_user/');
    expect(response).toEqual('test_response');
  });

  test('v3 user get businesses', async () => {
    const test_user = new User('test_biz_user', 'test_api_config', 'test_access_token');

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data')
    mock_request_data.mockResolvedValueOnce('test_businesses_response');

    const response = await test_user.get_businesses();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v3/users/test_biz_user/businesses/');
    expect(response).toEqual('test_businesses_response');
  });

  test('v3 user get boards and pins', async () => {
    const test_user = new User('test_user', 'test_api_config', 'test_access_token');

    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator')
    mock_get_iterator.mockResolvedValue('test_iterator');
    var iterator = await test_user.get_boards(
      {id: 'test_user_id'},
      {query_parameters: {key1: 'value1', key2: 'value2'}});
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[0][0]).toEqual('/v3/users/test_user_id/boards/feed/?key1=value1&key2=value2');

    iterator = await test_user.get_pins({id: 'test_user_id2'}, {});
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[1][0]).toEqual('/v3/users/test_user_id2/pins/');
  });
});