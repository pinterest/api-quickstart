import {ApiObject} from './api_object.js'
import got from 'got'

jest.mock('got');

describe('v3 api_object tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('v3 api_object request_data', async () => {
    const api_config = jest.fn();
    api_config.api_uri = 'test_uri';
    api_config.verbosity = 2;

    const access_token = jest.fn();
    access_token.header = jest.fn();
    access_token.header.mockReturnValueOnce('test_headers');

    got.get.mockResolvedValueOnce({'body': {'data': 'test_response_data'},
                                   'statusCode': 200
                                  });

    // check output
    console.log = jest.fn();
    
    const api_object = new ApiObject(api_config, access_token);
    const response = await api_object.request_data('/test_path');
    expect(response).toEqual('test_response_data');
    expect(got.get.mock.calls[0][0]).toEqual('test_uri/test_path');
    expect(got.get.mock.calls[0][1]).toEqual({'headers': 'test_headers',
                                              'responseType': 'json'});
    expect(console.log.mock.calls[0][0]).toEqual('<Response [200]>');
  });
});