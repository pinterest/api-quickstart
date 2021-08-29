import { Scope } from './v3/oauth_scope.js';
import get_auth_code from './user_auth.js';
import http from 'http';
import open from 'open';
import { v4 as uuidv4 } from 'uuid';

jest.mock('http');
jest.mock('open');
jest.mock('uuid');

describe('user_auth tests', () => {
  test('get_auth_code', async() => {
    const mock_api_config = jest.fn();
    mock_api_config.port = 'test-port';
    mock_api_config.oauth_uri = 'test-oauth-uri';
    mock_api_config.app_id = 'test-app-id';
    mock_api_config.landing_uri = 'test-landing-uri';
    mock_api_config.redirect_uri = 'test-redirect-uri';

    uuidv4.mockReturnValue('test-uuid');
    const mock_access_uri = '\
test-oauth-uri/oauth/?consumer_id=test-app-id\
&redirect_uri=test-redirect-uri\
&response_type=code&refreshable=true\
&scope=read_users,read_pins&state=test-uuid';

    // Used to verify that the user_auth code cleans the socket properly.
    const mock_socket = jest.fn();
    mock_socket.destroy = jest.fn();
    mock_socket.end = jest.fn();
    mock_socket.end.mockImplementation(callback => callback());

    // The mock_http_server is returned by the mock http.createServer.
    const mock_http_server = jest.fn();
    mock_http_server.close = jest.fn();
    mock_http_server.on = jest.fn().mockImplementation(
      (command, cb) => cb(mock_socket));
    mock_http_server.listen = jest.fn();

    // The mock request and response will be passed to the callback when
    // the user_auth code calls the mock open() function.
    const mock_request = jest.fn();
    mock_request.url = `\
${mock_api_config.redirect_uri}/?code=test-auth-code&state=test-uuid`;

    const mock_response = jest.fn();
    mock_response.writeHead = jest.fn();
    mock_response.end = jest.fn().mockImplementation(callback => callback());

    http.createServer.mockImplementation(callback => {
      // Save the callback so that it can be called by open().
      mock_http_server.callback = callback;
      return mock_http_server;
    });

    // The call to open() simulates the browser transaction by calling the request
    // processing function (callback) that was passed as an argument to createServer().
    open.mockImplementation(access_uri => {
      mock_http_server.callback(mock_request, mock_response);
    });

    const read_scopes = [Scope.READ_USERS, Scope.READ_PINS];
    const auth_code = await get_auth_code(
      mock_api_config, { scopes: read_scopes, refreshable: true }
    );
    expect(auth_code).toEqual('test-auth-code');
    expect(open.mock.calls[0][0]).toEqual(mock_access_uri);
    expect(mock_socket.destroy.mock.calls.length).toBe(1);
    expect(mock_http_server.on.mock.calls[0][0]).toEqual('connection');
    expect(mock_http_server.close.mock.calls.length).toBe(1);
    expect(mock_http_server.listen.mock.calls.length).toBe(1);
    expect(mock_response.writeHead.mock.calls[0][0]).toEqual(301);
    expect(mock_response.writeHead.mock.calls[0][1]).toEqual({ Location: 'test-landing-uri' });

    // verify that incorrect oauth state results in an error
    uuidv4.mockReturnValue('test-does-not-match');
    await expect(async() => {
      await get_auth_code(
        mock_api_config, { scopes: read_scopes, refreshable: true });
    }).rejects.toThrowError(
      new Error('Received OAuth state does not match sent state')
    );
  });
});
