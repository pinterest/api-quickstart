import unittest
from unittest import mock

import requests_mock

from src.v5.access_token import AccessToken


class AccessTokenTest(unittest.TestCase):
    @requests_mock.Mocker()
    @mock.patch("src.v5.access_token.get_auth_code")
    def test_access_token(self, rm, mock_get_auth_code):
        mock_get_auth_code.return_value = "test-auth-code"

        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.api_uri = "https://test-api-uri"
        mock_api_config.redirect_uri = "test-redirect-uri"
        mock_api_config.oauth_token_dir = "test-token-dir"
        mock_api_config.version = "v5"
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
