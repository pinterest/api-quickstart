import { ApiObject } from '../api_object.js';
import { Board } from './board.js';

jest.mock('../api_object');

describe('v5 board tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 board methods methods', async() => {
    const test_board = new Board('test_board_id', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    let response = await test_board.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/boards/test_board_id');
    expect(response).toEqual('test_response');

    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator');
    mock_get_iterator.mockResolvedValue('test_iterator');
    let iterator = await test_board.get_pins('query_parameters');
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[0]).toEqual([
      '/v5/boards/test_board_id/pins', 'query_parameters']);

    iterator = await test_board.get_sections();
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[1]).toEqual([
      '/v5/boards/test_board_id/sections', undefined]);

    iterator = await test_board.get_section_pins('test_section_id', 'query_parameters_2');
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[2]).toEqual([
      '/v5/boards/test_board_id/sections/test_section_id/pins',
      'query_parameters_2']);

    const board_data = {
      owner: { username: 'pindexter' },
      name: 'My Test Board',
      description: 'This is a test board'
    };
    expect('/pindexter/my-test-board/').toEqual(Board.text_id(board_data));

    const mock_post_data = jest.spyOn(ApiObject.prototype, 'post_data');
    const created_data = { id: 'created_board_id' };
    mock_post_data.mockResolvedValue(created_data);
    response = await test_board.create(board_data);
    expect(created_data).toEqual(response);
    expect(mock_post_data.mock.calls[0]).toEqual(
      ['/v5/boards',
        {
          name: 'My Test Board',
          description: 'This is a test board'
        // owner should not be in the data
        }]);

    created_data.id = 'created_section_id';
    const section_data = { name: 'New Section Name', ignore: 'ignored' };
    response = await test_board.create_section(section_data);

    expect(created_data).toEqual(response);
    expect(mock_post_data.mock.calls[1]).toEqual(
      ['/v5/boards/created_board_id/sections', // above create sets id that is tested here
        { name: 'New Section Name' }
      ]);

    const mock_delete_and_check = jest.spyOn(ApiObject.prototype, 'delete_and_check');
    await test_board.delete();
    expect(mock_delete_and_check.mock.calls[0][0]).toEqual('/v5/boards/created_board_id');
  });
});
