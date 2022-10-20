from unittest import mock

import requests_mock
from integration_mocks import IntegrationMocks


class GetAccessTokenTest(IntegrationMocks):
    # real_http is required for the redirect in integration_mocks to work
    @requests_mock.Mocker(real_http=True)
    @mock.patch("builtins.print")
    def test_get_access_token(self, rm, mock_print):
        rm.post(
            "https://api.pinterest.com/v5/oauth/token",
            json={
                "access_token": "test-access-token",
                "refresh_token": "test-refresh-token",
                "response_type": "authorization_code",
                "token_type": "bearer",
                "expires_in": "2592000",
                "refresh_token_expires_in": 31536000,
                "scope": "test-scope",
            },
        )
        rm.get(
            "https://api.pinterest.com/v5/user_account",
            json={
                "account_type": "BUSINESS",
                "profile_image": "test profile url",
                "website_url": "test website url",
                "username": "pindexterp",
            },
        )

        from scripts.get_access_token import main  # import here to see monkeypatches

        with mock.patch("builtins.open") as mock_open:
            with mock.patch.dict("os.environ", self.mock_os_environ, clear=True):
                mock_open.side_effect = FileNotFoundError  # no access_token.json file
                with self.mock_redirect():
                    main()  # run get_access_token

        # verify expected values printed. see unit tests for values
        mock_print.assert_any_call(
            "mock_open_new: "
            + "https://www.pinterest.com/oauth/?consumer_id=test-app-id"
            + "&redirect_uri=http://localhost:8085/&response_type=code"
            + "&refreshable=True"
            + "&scope=user_accounts:read,pins:read,boards:read"
            + "&state=test-token-hex"
        )
        mock_print.assert_any_call(
            "hashed access token: "
            + "597480d4b62ca612193f19e73fe4cc3ad17f0bf9cfc16a7cbf4b5064131c4805"
        )
        mock_print.assert_any_call(
            "hashed refresh token: "
            + "0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde"
        )
