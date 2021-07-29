import { ApiObject } from './api_object.js';
import got from 'got';

jest.mock('got');

describe('api_object tests', () => {
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
