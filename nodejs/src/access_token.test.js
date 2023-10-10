import fs from 'fs';
import got from 'got';

import { AccessToken } from './access_token.js';
import { Scope } from './oauth_scope.js';
import get_auth_code from './user_auth.js';

jest.mock('fs');
jest.mock('got');
jest.mock('./user_auth');

describe('v5 access_token tests', () => {
  const SAVED_ENV = process.env;

  beforeEach(() => {
    jest.clearAllMocks();
    process.env = {};
  });

  afterAll(() => {
    process.env = SAVED_ENV;
  });

  test('access token from environment', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.oauth_token_dir = 'test-token-dir';

    process.env.ACCESS_TOKEN_FROM_ENV = 'access token 42';
    const access_token = new AccessToken(mock_api_config,
      { name: 'access_token_from_env' });
    await access_token.fetch({});
    // echo -n 'access token 42' | shasum -a 256
    expect('553c1f363497ba07fecc989425e57e37c2b5f57ff7476c79dfd580ef0741db88')
      .toEqual(access_token.hashed());
  });

  test('access token from JSON file', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.oauth_token_dir = 'test-token-dir';

    const access_token_json = JSON.stringify({
      name: 'access_token_from_file',
      access_token: 'test access token from json',
      refresh_token: 'test refresh token from json',
      scopes: 'test-scope-1,test-scope-2'
    }, null, 2);

    // check output
    console.log = jest.fn();

    fs.readFileSync.mockReturnValue(access_token_json);
    const access_token = new AccessToken(mock_api_config,
      { name: 'access_token_from_file' });
    await access_token.fetch({});
    // echo -n 'test access token from json' | shasum -a 256
    expect('8de299eafa6932d8be18d7ff053d3bc6361c2b66ae1922f55fbf390d42de4cf6')
      .toEqual(access_token.hashed());

    // echo -n 'test refresh token from json' | shasum -a 256
    expect('15569cfd5a27881329e842dfea303e05ec60c99fbdebcdaa20d2445647297072')
      .toEqual(access_token.hashed_refresh_token());

    fs.open.mockImplementation((path, flags, mode, callback) => {
      expect(path).toEqual('test-token-dir/access_token_from_file.json');
      expect('w').toEqual(flags);
      expect(0o600).toEqual(mode);
      callback(null, 42);
    });

    fs.write.mockImplementation((fd, json, callback) => {
      expect(42).toEqual(fd);
      expect(access_token_json).toEqual(json);
      callback(null, json.length, json);
    });
    access_token.write();

    expect(console.log.mock.calls).toEqual([
      ['reading access_token_from_file from environment failed, trying read'],
      ['read access_token_from_file from test-token-dir/access_token_from_file.json']
    ]);
  });

  test('v5 access_token oauth', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.api_uri = 'test-api-uri';
    mock_api_config.redirect_uri = 'test-redirect-uri';
    mock_api_config.oauth_token_dir = 'test-token-dir';
    mock_api_config.verbosity = 2;

    const access_token = new AccessToken(mock_api_config, {});

    get_auth_code.mockResolvedValueOnce('test-auth-code');
    got.post.mockResolvedValueOnce({
      statusCode: 42,
      body: {
        status: 'test-status',
        scope: 'test-scope',
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token'
      }
    });

    // check output
    console.log = jest.fn();

    const read_scopes = [Scope.READ_USERS, Scope.READ_PINS];
    await access_token.oauth({ scopes: read_scopes });
    expect(get_auth_code.mock.calls[0][0]).toBe(mock_api_config);
    expect(get_auth_code.mock.calls[0][1]).toEqual({ scopes: read_scopes, refreshable: true });
    expect(got.post.mock.calls[0][0]).toEqual('test-api-uri/v5/oauth/token');
    expect(got.post.mock.calls[0][1]).toEqual({
      headers:
                                               {
                                                 Authorization:
                                                'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'
                                               },
      form: {
        code: 'test-auth-code',
        redirect_uri: 'test-redirect-uri',
        grant_type: 'authorization_code'
      },
      responseType: 'json'
    });
    expect(console.log.mock.calls).toEqual([
      ['getting auth_code...'],
      ['exchanging auth_code for access_token...'],
      ['POST', 'test-api-uri/v5/oauth/token'],
      ['<Response [42]>'],
      ['scope:', 'test-scope'],
      ['received refresh token']
    ]);
  });

  test('v5 access_token refresh without refresh_token', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.api_uri = 'test-api-uri-refresh';
    mock_api_config.redirect_uri = 'test-redirect-uri';
    mock_api_config.oauth_token_dir = 'test-token-dir';
    mock_api_config.verbosity = 2;

    const access_token_json = JSON.stringify({
      name: 'access_token_from_file',
      access_token: 'test access token from json',
      refresh_token: 'test refresh token from json',
      scopes: 'test-scope-1,test-scope-2'
    }, null, 2);

    fs.readFileSync.mockReturnValue(access_token_json);
    const access_token = new AccessToken(mock_api_config,
      { name: 'access_token_from_file' });
    await access_token.fetch({});

    // verify that the refresh token is not updated
    got.post.mockResolvedValueOnce({
      statusCode: 200,
      body: {
        access_token: 'test-refreshed-access-token-1'
      }
    });

    // check output
    console.log = jest.fn();

    await access_token.refresh({});
    expect(access_token.access_token).toEqual('test-refreshed-access-token-1'); // new
    expect(access_token.refresh_token).toEqual('test refresh token from json'); // unchanged
    expect(got.post.mock.calls[0][0]).toEqual('test-api-uri-refresh/v5/oauth/token');
    expect(got.post.mock.calls[0][1]).toEqual({
      headers:
                                               {
                                                 Authorization:
                                                'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'
                                               },
      form: {
        grant_type: 'refresh_token',
        refresh_token: 'test refresh token from json'
      },
      responseType: 'json'
    });
    expect(console.log.mock.calls).toEqual([
      ['refreshing access_token...'],
      ['POST', 'test-api-uri-refresh/v5/oauth/token'],
      ['<Response [200]>']
    ]);
  });

  test('v5 access_token refresh with chained refresh_token', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.api_uri = 'test-api-uri-refresh';
    mock_api_config.redirect_uri = 'test-redirect-uri';
    mock_api_config.oauth_token_dir = 'test-token-dir';
    mock_api_config.verbosity = 2;

    const access_token_json = JSON.stringify({
      name: 'access_token_from_file',
      access_token: 'test access token from json',
      refresh_token: 'test refresh token from json',
      scopes: 'test-scope-1,test-scope-2'
    }, null, 2);

    fs.readFileSync.mockReturnValue(access_token_json);
    const access_token = new AccessToken(mock_api_config,
      { name: 'access_token_from_file' });
    await access_token.fetch({});

    // verify that the refresh token is updated when provided by the API
    got.post.mockResolvedValueOnce({
      statusCode: 200,
      body: {
        access_token: 'test-refreshed-access-token-2',
        refresh_token: 'test-chained-refresh-token'
      }
    });

    // check output
    console.log = jest.fn();

    await access_token.refresh({ everlasting: true });
    expect(access_token.access_token).toEqual('test-refreshed-access-token-2'); // new
    expect(access_token.refresh_token).toEqual('test-chained-refresh-token'); // new
    expect(got.post.mock.calls[0][0]).toEqual('test-api-uri-refresh/v5/oauth/token');
    expect(got.post.mock.calls[0][1]).toEqual({
      headers:
                                               {
                                                 Authorization:
                                                'Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0'
                                               },
      form: {
        grant_type: 'refresh_token',
        refresh_token: 'test refresh token from json',
        refresh_on: true
      },
      responseType: 'json'
    });
    expect(console.log.mock.calls).toEqual([
      ['refreshing access_token...'],
      ['POST', 'test-api-uri-refresh/v5/oauth/token'],
      ['<Response [200]>'],
      ['received refresh token']
    ]);
  });
});
