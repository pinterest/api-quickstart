import unittest
import mock

from src.user_auth import get_auth_code
from src.user_auth import HTTPServerHandler
from src.v3.oauth_scope import Scope

class UserAuthTest(unittest.TestCase):

    @mock.patch('src.user_auth.ssl.wrap_socket')
    @mock.patch('src.user_auth.HTTPServer')
    @mock.patch('src.user_auth.open_new')
    def test_get_auth_code(self, mock_open_new, mock_http_server, mock_wrap_socket):

        class MockHttpServer:
            def __init__(self):
                self.socket = 'test-socket'

            def handle_request(self):
                self.auth_code = 'test-auth-code'

        mock_http_server_instance = MockHttpServer()
        mock_http_server.return_value = mock_http_server_instance

        mock_api_config = mock.Mock()
        mock_api_config.port = 'test-port'
        mock_api_config.oauth_uri = 'test-oauth-uri'
        mock_api_config.app_id = 'test-app-id'
        mock_api_config.redirect_uri = 'test-redirect-uri'
        mock_api_config.https_key_file = 'test-https-key-file'
        mock_api_config.https_cert_file = 'test-https-cert-file'
        mock_access_uri = ('test-oauth-uri/oauth/' +
                           '?consumer_id=test-app-id' +
                           '&redirect_uri=test-redirect-uri' +
                           '&response_type=code' +
                           '&refreshable=True')

        mock_wrap_socket.return_value = 'test-wrapped-socket'

        auth_code = get_auth_code(mock_api_config)
        mock_open_new.assert_called_once_with(mock_access_uri)
        mock_http_server.assert_called_once_with(('localhost', 'test-port'), mock.ANY)
        mock_wrap_socket.assert_called_once_with('test-socket',
                                                 certfile='test-https-cert-file',
                                                 keyfile='test-https-key-file',
                                                 server_side=True)
        self.assertEqual(mock_http_server_instance.socket, 'test-wrapped-socket')
        self.assertEqual(auth_code, 'test-auth-code')

        # verify calling get_auth_code with non-default values
        mock_open_new.reset_mock()
        mock_access_uri = ('test-oauth-uri/oauth/' +
                           '?consumer_id=test-app-id' +
                           '&redirect_uri=test-redirect-uri' +
                           '&response_type=code' +
                           # non-default values appear in the URI here
                           '&refreshable=False' +
                           '&scope=read_users,read_advertisers')
        auth_code = get_auth_code(mock_api_config,
                                  scopes=[Scope.READ_USERS,Scope.READ_ADVERTISERS],
                                  refreshable=False)
        mock_open_new.assert_called_once_with(mock_access_uri)

        # test clean exit when developer interrupts the web server on localhost with a KeyboardInterrupt
        class MockHttpServerInterrupted:
            def __init__(self):
                self.socket = 'test-socket'

            def handle_request(self):
                raise KeyboardInterrupt

        mock_http_server.return_value = MockHttpServerInterrupted()
        with self.assertRaisesRegex(SystemExit, "\nSorry that the OAuth redirect didn't work out. :-/"):
            auth_code = get_auth_code(mock_api_config)

    @mock.patch('src.user_auth.BaseHTTPRequestHandler.end_headers')
    @mock.patch('src.user_auth.BaseHTTPRequestHandler.send_header')
    @mock.patch('src.user_auth.BaseHTTPRequestHandler.send_response')
    @mock.patch('src.user_auth.super')
    def test_http_server_handler(self, mock_super,
                                 mock_send_response, mock_send_header, mock_end_headers):

        http_server_handler = HTTPServerHandler('test-request',
                                                'test-address',
                                                'test-server',
                                                'test-landing-uri')
        mock_super.assert_called_once()

        http_server_handler.path = 'test-path code=test-code'
        http_server_handler.server = mock.Mock()
        http_server_handler.server.auth_code = None

        http_server_handler.do_GET()
        mock_send_response.assert_called_once_with(301)
        mock_send_header.assert_called_once_with('Location', 'test-landing-uri')
        mock_end_headers.assert_called_once_with()
        self.assertEqual(http_server_handler.server.auth_code, 'test-code')
