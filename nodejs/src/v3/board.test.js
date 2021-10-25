import { ApiObject } from '../api_object.js';
import { Board } from './board.js';

jest.mock('../api_object');

describe('v3 board tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 board methods', async() => {
    const test_board = new Board('test_board_id', 'test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');

    let response = await test_board.get();
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v3/boards/test_board_id/');
    expect(response).toEqual('test_response');

    const mock_get_iterator = jest.spyOn(ApiObject.prototype, 'get_iterator');
    mock_get_iterator.mockResolvedValue('test_iterator');
    let iterator = await test_board.get_pins('query_parameters');
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[0]).toEqual([
      '/v3/boards/test_board_id/pins/', 'query_parameters']);

    iterator = await test_board.get_sections();
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[1]).toEqual([
      '/v3/board/test_board_id/sections/', undefined]);

    iterator = await test_board.get_section_pins('test_section_id', 'query_parameters_2');
    expect('test_iterator').toEqual(iterator);
    expect(mock_get_iterator.mock.calls[2]).toEqual([
      '/v3/board/sections/test_section_id/pins/',
      'query_parameters_2']);

    const board_data = {
      name: 'My Test Board',
      description: 'This is a test board',
      category: 'fashion',
      url: '/pindexter/my-test-board/'
    };
    expect('/pindexter/my-test-board/').toEqual(Board.text_id(board_data));

    const mock_put_data = jest.spyOn(ApiObject.prototype, 'put_data');
    const created_data = { id: 'created_board_id' };
    mock_put_data.mockResolvedValue(created_data);
    response = await test_board.create(board_data);
    expect(created_data).toEqual(response);
    expect(mock_put_data.mock.calls[0]).toEqual(
      ['/v3/boards/',
        {
          name: 'My Test Board',
          description: 'This is a test board',
          category: 'fashion'
        // url should not be in the data
        }]);

    created_data.id = 'created_section_id';
    const section_data = { title: 'New Section Name', ignore: 'ignored', title_source: '1' };
    response = await test_board.create_section(section_data);

    // Note: the create() above sets test_board.id to the created board
    expect(created_data).toEqual(response);
    expect(mock_put_data.mock.calls[1]).toEqual(
      ['/v3/board/created_board_id/sections/',
        { title: 'New Section Name', title_source: '1' }
        // ignored key/value should not be in the data
      ]);

    const mock_delete_and_check = jest.spyOn(ApiObject.prototype, 'delete_and_check');
    await test_board.delete();
    expect(mock_delete_and_check.mock.calls[0][0]).toEqual('/v3/boards/created_board_id/');
  });
});
