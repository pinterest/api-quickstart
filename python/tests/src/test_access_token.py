import json
import unittest
from unittest import mock

import requests_mock

from access_token import AccessToken


class AccessTokenTest(unittest.TestCase):
    mock_os_environ_access_token = {"ACCESS_TOKEN_FROM_ENV": "access token 42"}

    @mock.patch.dict("os.environ", mock_os_environ_access_token, clear=True)
    def test_access_token_from_environment(self):
        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.oauth_token_dir = "test-token-dir"

        # The name of the access token is converted to upper case to find
        # it in the process environment.
        access_token = AccessToken(mock_api_config, name="access_token_from_env")
        access_token.fetch()
        # echo -n 'access token 42' | shasum -a 256
        self.assertEqual(
            access_token.hashed(),
            "553c1f363497ba07fecc989425e57e37c2b5f57ff7476c79dfd580ef0741db88",
        )
        with self.assertRaisesRegex(
            RuntimeError, "AccessToken does not have a refresh token"
        ):
            access_token.hashed_refresh_token()

    mock_os_environ_empty = {}

    @mock.patch.dict("os.environ", mock_os_environ_empty, clear=True)
    @mock.patch("os.chmod")
    @mock.patch("builtins.open")
    def test_access_token_from_json(self, mock_open, mock_chmod):

        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.oauth_token_dir = "test-token-dir"

        access_token_dict = {
            "name": "access_token_from_file",
            "access_token": "test access token from json",
            "refresh_token": "test refresh token from json",
            "scopes": "test-scope-1,test-scope-2",
        }

        # Test access token JSON file read
        mock_json_file = mock.Mock()
        mock_json_file.read.return_value = json.dumps(access_token_dict)
        mock_json_file.fileno.return_value = 42
        # mocking __enter__ is required because open is used in a context manager
        mock_open.return_value.__enter__.return_value = mock_json_file

        access_token = AccessToken(mock_api_config, name="access_token_from_file")
        access_token.fetch()
        # echo -n 'test access token from json' | shasum -a 256
        self.assertEqual(
            access_token.hashed(),
            "8de299eafa6932d8be18d7ff053d3bc6361c2b66ae1922f55fbf390d42de4cf6",
        )
        # echo -n 'test refresh token from json' | shasum -a 256
        self.assertEqual(
            access_token.hashed_refresh_token(),
            "15569cfd5a27881329e842dfea303e05ec60c99fbdebcdaa20d2445647297072",
        )

        # Test access token JSON file write
        self.mock_write_text = ""

        def mock_write_json(text):  # write to a string instead of a file
            self.mock_write_text += text

        mock_json_file.write = mock_write_json

        access_token.write()
        mock_chmod.assert_called_once_with(42, 0o600)
        self.assertEqual(json.loads(self.mock_write_text), access_token_dict)

    @requests_mock.Mocker()
    @mock.patch("access_token.get_auth_code")
    def test_access_token(self, rm, mock_get_auth_code):
        mock_get_auth_code.return_value = "test-auth-code"

        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.api_uri = "https://test-api-uri"
        mock_api_config.redirect_uri = "test-redirect-uri"
        mock_api_config.oauth_token_dir = "test-token-dir"
        mock_api_config.verbosity = 2

        rm.post(
            "https://test-api-uri/v5/oauth/token",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            json={
                "status": "test-status",
                "scope": "test-scope",
                "access_token": "test-access-token",
                "refresh_token": "test-refresh-token",
            },
        )
        access_token = AccessToken(mock_api_config)
        access_token.oauth()

        # mock does not figure out enum equality, so need to unpack arguments
        # of get_auth_code in order to check the default value for scopes.
        self.assertTrue(mock_get_auth_code.mock_calls[0][2]["refreshable"])
        scopes = mock_get_auth_code.mock_calls[0][2]["scopes"]
        # convert from Scope enum to values
        values = list(map(lambda scope: scope.value, scopes))
        # verify the scopes used by the API
        self.assertEqual(["user_accounts:read", "pins:read", "boards:read"], values)
        self.assertEqual(
            rm.last_request.text,
            "code=test-auth-code"
            + "&redirect_uri=test-redirect-uri"
            + "&grant_type=authorization_code",
        )

        rm.post(
            "https://test-api-uri/v5/oauth/token",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            headers={"x-pinterest-rid": "mock-request-id"},
            json={
                "access_token": "pina_new-access-token",
                "refresh_token": "pinr_new-refresh-token",
                "scope": "users:read,pins:read,boards:read",
            },
        )

        # verify that refresh works by using the sha256 of 'pina_new-access-token'
        access_token.refresh()
        # echo -n pina_new-access-token | shasum -a 256
        self.assertEqual(
            access_token.hashed(),
            "4e9a163e7e33428d50c6eda1305fa8f316aa9779578944ca5db4748acd22e8d2",
        )
        self.assertEqual(
            rm.last_request.text,
            "grant_type=refresh_token" + "&refresh_token=test-refresh-token",
        )

        # verify behavior with non-default arguments:
        # - scopes passed to get_auth_code
        # - refresh raises an exception
        rm.post(
            "https://test-api-uri/v5/oauth/token",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            headers={"x-pinterest-rid": "mock-request-id"},
            json={
                "status": "test-stats",
                "scope": "users:read,pins:read,boards:read",
                "access_token": "test-access-token",
                "refresh_token": "pinr_test-refresh-token",
            },
        )
        mock_get_auth_code.reset_mock()
        access_token = AccessToken(mock_api_config)
        access_token.oauth(scopes=["test-scope-1", "test-scope-2"], refreshable=True)
        mock_get_auth_code.assert_called_once_with(
            mock_api_config, scopes=["test-scope-1", "test-scope-2"], refreshable=True
        )

        with self.assertRaisesRegex(
            ValueError, "Pinterest API v5 only provides refreshable OAuth access tokens"
        ):
            access_token.oauth(refreshable=False)
