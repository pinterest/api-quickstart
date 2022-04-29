from unittest import mock

import requests_mock
from integration_mocks import IntegrationMocks


class GetBusinessesTest(IntegrationMocks):
    # real_http is required for the redirect in integration_mocks to work
    @requests_mock.Mocker(real_http=True)
    @mock.patch("builtins.print")
    def test_get_businesses(self, rm, mock_print):
        rm.put(
            "https://api.pinterest.com/v3/oauth/access_token/",
            json={
                "status": "test-status",
                "scope": "test-scope",
                "access_token": "test-access-token",
                "data": {"refresh_token": "test-refresh-token"},
            },
        )
        rm.get(
            "https://api.pinterest.com/v3/users/me/",
            json={
                "data": {
                    "full_name": "test fullname",
                    "id": "test user id",
                    "about": "test about",
                    "profile_url": "test profile url",
                    "pin_count": "pin count",
                }
            },
        )
        rm.get(
            "https://api.pinterest.com/v3/users/me/businesses/",
            json={
                "data": {
                    "full_name": "test business name",
                    "id": "test-business-id-number",
                }
            },
        )

        from scripts.get_businesses import main  # import here to see monkeypatches

        with mock.patch("builtins.open") as mock_open:
            with mock.patch.dict("os.environ", self.mock_os_environ, clear=True):
                mock_open.side_effect = FileNotFoundError  # no access_token.json file
                with self.mock_redirect():
                    main()  # run get_businesses

        # verify expected output
        mock_print.assert_any_call("Full Name: test fullname")
        mock_print.assert_any_call(
            {"full_name": "test business name", "id": "test-business-id-number"}
        )
