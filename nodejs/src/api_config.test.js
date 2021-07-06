import {ApiConfig} from './api_config';

describe('ApiConfig test environment', () => {
  const SAVED_ENV = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = {}
  });

  afterAll(() => {
    process.env = SAVED_ENV;
  });

  test('API configuration from defaults', () => {
    // check output
    console.log = jest.fn();

    // minimal environment
    process.env.PINTEREST_APP_ID = 'test-app-id';
    process.env.PINTEREST_APP_SECRET = 'test-app-secret';
    const api_config = new ApiConfig({});

    expect(api_config.app_id).toEqual('test-app-id');
    expect(api_config.app_secret).toEqual('test-app-secret');
    expect(api_config.port).toEqual(8085);
    expect(api_config.redirect_uri).toEqual('http://localhost:8085/');
    expect(api_config.landing_uri).toEqual('https://developers.pinterest.com/manage/test-app-id');
    expect(api_config.oauth_uri).toEqual('https://www.pinterest.com');
    expect(api_config.api_uri).toEqual('https://api.pinterest.com');
    expect(api_config.version).toEqual('v3');
    expect(console.log.mock.calls[0][0]).toEqual(
      'Using application ID and secret from PINTEREST_APP_ID and PINTEREST_APP_SECRET.');
  });

  test('environment API environment', () => {
    // check output
    console.log = jest.fn();

    // minimal environment
    process.env.PINTEREST_APP_ID = 'test-app-id';
    process.env.PINTEREST_APP_SECRET = 'test-app-secret';
    process.env.PINTEREST_APP_ID = 'test-app-id';
    process.env.PINTEREST_APP_SECRET = 'test-app-secret';
    process.env.REDIRECT_LANDING_URI = 'test-landing-uri';
    process.env.PINTEREST_OAUTH_URI = 'test-oauth-uri';
    process.env.PINTEREST_API_URI = 'test-api-uri';
    process.env.PINTEREST_API_VERSION = 'test-api-version';
    const api_config = new ApiConfig({});

    expect(api_config.app_id).toEqual('test-app-id');
    expect(api_config.app_secret).toEqual('test-app-secret');
    expect(api_config.port).toEqual(8085);
    expect(api_config.redirect_uri).toEqual('http://localhost:8085/');
    expect(api_config.landing_uri).toEqual('test-landing-uri');
    expect(api_config.oauth_uri).toEqual('test-oauth-uri');
    expect(api_config.api_uri).toEqual('test-api-uri');
    expect(api_config.version).toEqual('test-api-version');
    expect(console.log.mock.calls[0][0]).toEqual(
      'Using application ID and secret from PINTEREST_APP_ID and PINTEREST_APP_SECRET.');
  });
});
