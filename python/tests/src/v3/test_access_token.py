import unittest
from unittest import mock

import requests_mock

from src.v3.access_token import AccessToken


class AccessTokenTest(unittest.TestCase):
    @requests_mock.Mocker()
    @mock.patch("src.v3.access_token.get_auth_code")
    def test_access_token(self, rm, mock_get_auth_code):
        mock_get_auth_code.return_value = "test-auth-code"

        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.api_uri = "https://test-api-uri"
        mock_api_config.redirect_uri = "test-redirect-uri"
        mock_api_config.oauth_token_dir = "test-token-dir"
        mock_api_config.version = "v3"
        mock_api_config.verbosity = 2

        rm.put(
            "https://test-api-uri/v3/oauth/access_token/",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            json={
                "status": "test-status",
                "scope": "test-scope",
                "access_token": "test-access-token",
                "data": {"refresh_token": "test-refresh-token"},
            },
        )
        access_token = AccessToken(mock_api_config)
        access_token.oauth()
        mock_get_auth_code.assert_called_once_with(
            mock_api_config, scopes=None, refreshable=True
        )
        self.assertEqual(
            "code=test-auth-code"
            + "&redirect_uri=test-redirect-uri"
            + "&grant_type=authorization_code",
            rm.last_request.text,
        )

        # header() should create a new headers dict if required
        test_header = {"Authorization": "Bearer test-access-token"}
        header = access_token.header()
        self.assertEqual(header, test_header)

        # header() should merge with an existing headers dict and return it
        headers = {"this key": "this value"}
        expected = headers.copy()
        expected.update(test_header)
        returned = access_token.header(headers=headers)
        self.assertEqual(headers, expected)
        self.assertEqual(headers, returned)

        # verify that the SHA256 hash works
        # echo -n test-access-token | shasum -a 256
        self.assertEqual(
            access_token.hashed(),
            "597480d4b62ca612193f19e73fe4cc3ad17f0bf9cfc16a7cbf4b5064131c4805",
        )
        # echo -n test-refresh-token | shasum -a 256
        self.assertEqual(
            access_token.hashed_refresh_token(),
            "0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde",
        )

        rm.put(
            "https://test-api-uri/v3/oauth/access_token/",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            headers={"x-pinterest-rid": "mock-request-id"},
            json={"access_token": "new-access-token"},
        )

        # verify that refresh works by using the sha256 of 'new-access-token'
        access_token.refresh()
        # echo -n new-access-token | shasum -a 256
        self.assertEqual(
            access_token.hashed(),
            "25b416c373e247768cc1a3ed4a20a13888f6b9f5288378f4756ce227d05b7710",
        )
        self.assertEqual(
            "grant_type=refresh_token&refresh_token=test-refresh-token",
            rm.last_request.text,
        )

        # verify behavior with non-default arguments:
        # - scopes passed to get_auth_code
        # - refresh raises an exception
        rm.put(
            "https://test-api-uri/v3/oauth/access_token/",
            request_headers={
                "Authorization": "Basic dGVzdC1hcHAtaWQ6dGVzdC1hcHAtc2VjcmV0"
            },
            headers={"x-pinterest-rid": "mock-request-id"},
            json={
                "status": "test-status",
                "scope": "test-scope-1,test-scope-2",
                "access_token": "test-access-token",
                "data": {},
            },
        )
        mock_get_auth_code.reset_mock()
        access_token = AccessToken(mock_api_config)
        access_token.oauth(scopes=["test-scope-1", "test-scope-2"], refreshable=False)
        mock_get_auth_code.assert_called_once_with(
            mock_api_config, scopes=["test-scope-1", "test-scope-2"], refreshable=False
        )
        with self.assertRaisesRegex(
            RuntimeError, "AccessToken does not have a refresh token"
        ):
            access_token.refresh()
