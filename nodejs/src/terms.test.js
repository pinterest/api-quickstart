import { ApiObject } from './api_object.js';
import { Terms } from './terms.js';

jest.mock('./api_object');

describe('v5 terms tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v5 related terms methods', async() => {
    const test_terms = new Terms('test_api_config', 'test_access_token');
    expect(ApiObject.mock.instances.length).toBe(1);
    expect(ApiObject.mock.calls[0]).toEqual(['test_api_config', 'test_access_token']);

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');
    const mock_add_query = jest.spyOn(ApiObject.prototype, 'add_query');
    mock_add_query.mockReturnValue('/v5/terms/related?terms=test_terms');

    const response = await test_terms.get_related('test_terms');
    expect(mock_add_query.mock.calls[0]).toEqual(['/v5/terms/related', { terms: 'test_terms' }]);
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/terms/related?terms=test_terms');
    expect(response).toEqual('test_response');
  });

  test('v5 suggested terms methods with no limit', async() => {
    const test_terms = new Terms('test_api_config', 'test_access_token');

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');
    const mock_add_query = jest.spyOn(ApiObject.prototype, 'add_query');
    mock_add_query.mockReturnValue('/v5/terms/suggested?term=test_terms');

    const response = await test_terms.get_suggested('test_term', {});
    expect(mock_add_query.mock.calls[0]).toEqual(['/v5/terms/suggested', { term: 'test_term' }]);
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/terms/suggested?term=test_terms');
    expect(response).toEqual('test_response');
  });

  test('v5 suggested terms methods with limit', async() => {
    const test_terms = new Terms('test_api_config', 'test_access_token');

    const mock_request_data = jest.spyOn(ApiObject.prototype, 'request_data');
    mock_request_data.mockResolvedValue('test_response');
    const mock_add_query = jest.spyOn(ApiObject.prototype, 'add_query');
    mock_add_query.mockReturnValue('/v5/terms/suggested?term=test_terms&limit=5');

    const response = await test_terms.get_suggested('test_term', { limit: 5 });
    expect(mock_add_query.mock.calls[0]).toEqual(['/v5/terms/suggested', { term: 'test_term', limit: 5 }]);
    expect(mock_request_data.mock.calls[0][0]).toEqual('/v5/terms/suggested?term=test_terms&limit=5');
    expect(response).toEqual('test_response');
  });
});
