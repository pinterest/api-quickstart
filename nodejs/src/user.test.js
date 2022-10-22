import { ApiObject } from './api_object.js';
import { Board } from './board.js';
import { User } from './user.js';

jest.mock('./api_object');
jest.mock('./board');

describe('v5 user tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 user get methods', async() => {
    const test_user = new User('test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    // Mocking the response from request_data in the instantiated copy of ApiObject
    // does not work, because User is a subclass of (extends) ApiObject. This would
    // work if User contained an ApiObject. (Had a "Has-A relationship" with ApiObject
    // instead of being a subclass.
    // const mock_request_data = ApiObject.mock.instances[0].request_data;

    // Instead of using the mock in the instance, need to use spyOn because User is a
    // subclass (extends) ApiObject.
    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    const response = await test_user.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/user_account');
    expect(response).toEqual('test_response');

    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator');
    mock_get_iterator.mockResolvedValue('test_iterator');
    const iterator = await test_user.get_boards('test_user_data', 'query_parameters');
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[0]).toEqual([
      '/v5/boards', 'query_parameters']);
  });

  test('v5 user get pins', async() => {
    const test_user = new User('test_api_config', 'test_access_token');

    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator');
    // This value mocks the iterator in the get_boards() call.
    mock_get_iterator.mockResolvedValue([
      { id: 'board1_id' }, { id: 'board2_id' }, { id: 'board3_id' }
    ]);
    const mock_get_pins = jest.spyOn(Board.prototype, 'get_pins');
    mock_get_pins
      .mockResolvedValueOnce(['board1_pin1', 'board1_pin2']) // board 1
      .mockResolvedValueOnce([]) // board 2, no pins
      .mockResolvedValueOnce(['board3_pin1']); // board 3

    const expected_pins = ['board1_pin1', 'board1_pin2', 'board3_pin1'];
    let index = 0;
    const pin_iterator = await test_user.get_pins('test_user_data', {});
    for await (const pin_data of pin_iterator) {
      expect(pin_data).toEqual(expected_pins[index]);
      index++;
    }
    expect(Board.mock.instances.length).toBe(3); // 3 board objects created
    expect(Board.mock.calls[0][0]).toEqual('board1_id');
    expect(Board.mock.calls[1][0]).toEqual('board2_id');
    expect(Board.mock.calls[2][0]).toEqual('board3_id');
  });
});
