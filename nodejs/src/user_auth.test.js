import {Scope} from './oauth_scope.js'
import get_auth_code from './user_auth.js'
import https from 'https'
import fs from 'fs'
import open from 'open'

jest.mock('https');
jest.mock('fs');
jest.mock('open');

describe('user_auth tests', () => {
  test('test get_auth_code', async () => {
    const mock_api_config = jest.fn();
    mock_api_config.port = 'test-port';
    mock_api_config.oauth_uri = 'test-oauth-uri';
    mock_api_config.app_id = 'test-app-id'
    mock_api_config.landing_uri = 'test-landing-uri';
    mock_api_config.redirect_uri = 'test-redirect-uri';
    mock_api_config.https_key_file = 'test-https-key-file';
    mock_api_config.https_cert_file = 'test-https-cert-file';
    const mock_access_uri = ('test-oauth-uri/oauth/' +
                             '?consumer_id=test-app-id' +
                             '&redirect_uri=test-redirect-uri' +
                             '&response_type=code' +
                             '&refreshable=true' +
                             '&scope=read_users,read_pins');

    fs.readFileSync.mockImplementation(filename => {
      if (filename == 'test-https-key-file') {
        return 'test-https-key';
      } else if (filename == 'test-https-cert-file') {
        return 'test-https-cert';
      } else {
        throw `readFileSync received unexpect filename: ${filename}`;
      }
    });

    const mock_socket = jest.fn();
    mock_socket.destroy = jest.fn();
    mock_socket.end = jest.fn();
    mock_socket.end.mockImplementation(callback => callback());

    const mock_http_server = jest.fn();
    mock_http_server.close = jest.fn();
    mock_http_server.on = jest.fn();
    mock_http_server.on.mockImplementation((command, cb) => cb(mock_socket));
    mock_http_server.listen = jest.fn();

    const mock_request = jest.fn();
    mock_request.url = mock_api_config.redirect_uri + '/?code=test-auth-code';
    const mock_response = jest.fn();
    mock_response.writeHead = jest.fn();
    mock_response.end = jest.fn();
    mock_response.end.mockImplementation(callback => callback());

    https.createServer.mockImplementation((options, callback) => {
      mock_http_server.callback = callback;
      return mock_http_server;
    });

    open.mockImplementation(access_uri => {
      mock_http_server.callback(mock_request, mock_response)
    });

    const read_scopes = [Scope.READ_USERS,Scope.READ_PINS];
    const auth_code = await get_auth_code(mock_api_config, {scopes: read_scopes, refreshable: true});
    expect(auth_code).toEqual('test-auth-code');
    expect(open.mock.calls[0][0]).toEqual(mock_access_uri);
    expect(https.createServer.mock.calls[0][0]).toEqual({key: 'test-https-key',
                                                         cert: 'test-https-cert'});
    expect(mock_socket.destroy.mock.calls.length).toBe(1);
    expect(mock_http_server.on.mock.calls[0][0]).toEqual('connection');
    expect(mock_http_server.close.mock.calls.length).toBe(1);
    expect(mock_response.writeHead.mock.calls[0][0]).toEqual(301);
    expect(mock_response.writeHead.mock.calls[0][1]).toEqual({'Location': 'test-landing-uri'});
  });
});