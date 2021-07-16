import fs from 'fs'
import {AccessTokenCommon} from './access_token_common.js'

jest.mock('fs')

describe('access_token_common tests', () => {
  const SAVED_ENV = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = {}
  });

  afterAll(() => {
    process.env = SAVED_ENV;
  });

  test('access token from environment', async () => {
    const mock_api_config = jest.fn();
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.app_secret = 'test-app-secret';
    mock_api_config.oauth_token_dir = 'test-token-dir';


    process.env.ACCESS_TOKEN_FROM_ENV = 'access token 42';
    var access_token = new AccessTokenCommon(mock_api_config,
                                             {name: 'access_token_from_env'});
    await access_token.fetch({});
    // echo -n 'access token 42' | shasum -a 256
    expect('553c1f363497ba07fecc989425e57e37c2b5f57ff7476c79dfd580ef0741db88')
      .toEqual(access_token.hashed());

    mock_api_config.version = 'v3'
    access_token = new AccessTokenCommon(mock_api_config, {});
    process.env.ACCESS_TOKEN_V3 = 'v3 access token';
    await access_token.fetch({});
    // echo -n 'access token 42' | shasum -a 256
    expect('0186dba9997e23d7e180a711417e529e8647b2b296807d26781dc76b6edb726e')
      .toEqual(access_token.hashed());

  });

  test('access token from JSON file', async () => {
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
    const access_token = new AccessTokenCommon(mock_api_config,
                                               {name: 'access_token_from_file'});
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
});