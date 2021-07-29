import { AccessToken } from './access_token.js';
import { Scope } from './oauth_scope.js';
import get_auth_code from '../user_auth.js';
import got from 'got';

jest.mock('../user_auth');
jest.mock('got');

describe('v5 access_token tests', () => {
  test('v5 api_object request_data', async() => {
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
});
