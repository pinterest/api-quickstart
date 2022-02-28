import { ApiObject } from './api_object.js';
import got from 'got';

jest.mock('got');

/*
 * Tests for the generic ApiObject class that is used for all versions
 * of the Pinterest API.
 *
 * Note: the reset_backoff and wait_backoff functions are tested with
 * the classes that call these functions instead of testing them in
 * this file.
 */
describe('api_object tests', () => {
  test('add_query', () => {
    const api_object = new ApiObject(jest.fn(), jest.fn());

    // cases with no parameters to be added
    expect(api_object.add_query('hello')).toBe('hello');
    expect(api_object.add_query('hello', null)).toBe('hello');
    expect(api_object.add_query('hello', {})).toBe('hello');
    expect(api_object.add_query('hello', { query_parameters: {} })).toBe('hello');

    // verify that different numbers of parameters work
    expect(api_object.add_query('hello', { world: 'ready' }))
      .toBe('hello?world=ready');

    expect(api_object.add_query('hello', {
      world: 'ready',
      set: 'go'
    })).toBe('hello?world=ready&set=go');

    expect(api_object.add_query('hello', {
      world: 'ready',
      set: 'go',
      eeny: 'meeny'
    })).toBe('hello?world=ready&set=go&eeny=meeny');

    // verify that query_parameters are surfaced from within object
    expect(api_object.add_query('hello', {
      query_parameters: {
        world: 'ready',
        set: 'go',
        eeny: 'meeny'
      }
    })).toBe('hello?world=ready&set=go&eeny=meeny');

    // verify that delimiter works properly when there already
    // parameters in the path
    expect(api_object.add_query('hello?goodbye', { cruel: 'world' }))
      .toBe('hello?goodbye&cruel=world');

    expect(api_object.add_query('hello?good=bye', {
      cruel: 'world',
      and: 'farewell'
    }))
      .toBe('hello?good=bye&cruel=world&and=farewell');
  });

  test('v3 api_object', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.api_uri = 'test_uri';
    mock_api_config.verbosity = 2;
    mock_api_config.version = 'v3';

    const mock_access_token = jest.fn();
    mock_access_token.header = jest.fn();
    mock_access_token.header.mockReturnValueOnce('test_headers');

    got.get.mockResolvedValueOnce({
      body: { data: 'test_response_data' },
      statusCode: 200
    });

    // check output
    console.log = jest.fn();

    const api_object = new ApiObject(mock_api_config, mock_access_token);
    const response = await api_object.request_data('/test_path');
    expect(response).toEqual('test_response_data');
    expect(got.get.mock.calls[0][0]).toEqual('test_uri/test_path');
    expect(got.get.mock.calls[0][1]).toEqual({
      headers: 'test_headers',
      followRedirect: false,
      responseType: 'json'
    });
    expect(console.log.mock.calls[0]).toEqual(['GET', 'test_uri/test_path']);
    expect(console.log.mock.calls[1][0]).toEqual('<Response [200]>');
  });

  test('v5 api_object', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.api_uri = 'test_uri';
    mock_api_config.verbosity = 2;
    mock_api_config.version = 'v5';

    const mock_access_token = jest.fn();
    mock_access_token.header = jest.fn();
    mock_access_token.header.mockReturnValueOnce('test_headers');

    got.get.mockResolvedValueOnce({
      body: 'test_response_data',
      statusCode: 200
    });

    // check output
    console.log = jest.fn();

    const api_object = new ApiObject(mock_api_config, mock_access_token);
    const response = await api_object.request_data('/test_path');
    expect(response).toEqual('test_response_data');
  });
});
