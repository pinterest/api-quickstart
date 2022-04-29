import unittest
from unittest import mock

from user_auth import HTTPServerHandler, get_auth_code
from v3.oauth_scope import Scope


class UserAuthTest(unittest.TestCase):
    @mock.patch("user_auth.secrets.token_hex")
    @mock.patch("user_auth.HTTPServer")
    @mock.patch("user_auth.open_new")
    def test_get_auth_code(self, mock_open_new, mock_http_server, mock_token_hex):
        class MockHttpServer:
            def __init__(self):
                self.socket = "test-socket"

            def handle_request(self):
                self.auth_code = "test-auth-code"

        mock_http_server_instance = MockHttpServer()
        mock_http_server.return_value = mock_http_server_instance
        mock_token_hex.return_value = "test-token-hex"

        mock_api_config = mock.Mock()
        mock_api_config.port = "test-port"
        mock_api_config.oauth_uri = "test-oauth-uri"
        mock_api_config.app_id = "test-app-id"
        mock_api_config.redirect_uri = "test-redirect-uri"
        mock_api_config.verbosity = 2
        mock_access_uri = (
            "test-oauth-uri/oauth/"
            + "?consumer_id=test-app-id"
            + "&redirect_uri=test-redirect-uri"
            + "&response_type=code"
            + "&refreshable=True"
            + "&state=test-token-hex"
        )

        auth_code = get_auth_code(mock_api_config)
        mock_open_new.assert_called_once_with(mock_access_uri)
        mock_http_server.assert_called_once_with(("localhost", "test-port"), mock.ANY)
        self.assertEqual(mock_http_server_instance.socket, "test-socket")
        self.assertEqual(auth_code, "test-auth-code")

        # verify calling get_auth_code with non-default values
        mock_open_new.reset_mock()
        mock_access_uri = (
            "test-oauth-uri/oauth/"
            + "?consumer_id=test-app-id"
            + "&redirect_uri=test-redirect-uri"
            + "&response_type=code"
            +
            # non-default values appear in the URI here
            "&refreshable=False"
            + "&scope=read_users,read_advertisers"
            + "&state=test-token-hex"
        )
        auth_code = get_auth_code(
            mock_api_config,
            scopes=[Scope.READ_USERS, Scope.READ_ADVERTISERS],
            refreshable=False,
        )
        mock_open_new.assert_called_once_with(mock_access_uri)

        # test clean exit when developer interrupts the web server
        # on localhost with a KeyboardInterrupt
        class MockHttpServerInterrupted:
            def __init__(self):
                self.socket = "test-socket"

            def handle_request(self):
                raise KeyboardInterrupt

        mock_http_server.return_value = MockHttpServerInterrupted()
        with self.assertRaisesRegex(
            SystemExit, "\nSorry that the OAuth redirect didn't work out. :-/"
        ):
            auth_code = get_auth_code(mock_api_config)

    @mock.patch("user_auth.BaseHTTPRequestHandler.end_headers")
    @mock.patch("user_auth.BaseHTTPRequestHandler.send_header")
    @mock.patch("user_auth.BaseHTTPRequestHandler.send_response")
    @mock.patch("user_auth.super")
    def test_http_server_handler(
        self, mock_super, mock_send_response, mock_send_header, mock_end_headers
    ):

        mock_api_config = mock.Mock()
        mock_api_config.landing_uri = "test-landing-uri"
        mock_api_config.verbosity = 2

        http_server_handler = HTTPServerHandler(
            "test-request",
            "test-address",
            "test-server",
            mock_api_config,
            "test-secret",
        )
        mock_super.assert_called_once()

        http_server_handler.path = "test-path?code=test-code&state=test-secret"
        http_server_handler.server = mock.Mock()
        http_server_handler.server.auth_code = None

        http_server_handler.do_GET()
        mock_send_response.assert_called_once_with(301)
        mock_send_header.assert_called_once_with("Location", "test-landing-uri")
        mock_end_headers.assert_called_once_with()
        self.assertEqual(http_server_handler.server.auth_code, "test-code")

        # verify the error when the OAuth state does not match
        http_server_handler.path = "test-path?code=test-code&state=wrong-test-secret"
        with self.assertRaisesRegex(
            RuntimeError, "Received OAuth state does not match sent state"
        ):
            http_server_handler.do_GET()

        # verify the error when the redirect does not contain an authorization code
        http_server_handler.path = "test-path?state=test-secret"
        with self.assertRaisesRegex(
            RuntimeError, "OAuth redirect does not have an auth code"
        ):
            http_server_handler.do_GET()
