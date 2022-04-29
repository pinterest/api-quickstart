from unittest import mock

import requests_mock
from integration_mocks import IntegrationMocks


class RefreshExampleTest(IntegrationMocks):
    # real_http is required for the redirect in integration_mocks to work
    @requests_mock.Mocker(real_http=True)
    @mock.patch("time.sleep")  # prevent delay from real sleep
    @mock.patch("builtins.print")
    def test_refresh_example(self, rm, mock_print, mock_sleep):
        # set up 4 different responses to
        # PUT https://api.pinterest.com/v3/oauth/access_token/
        basic_response = {
            "status": "test-status",
            "scope": "test-scope",
            "access_token": "REPLACE ME",
            "data": {"refresh_token": "test-refresh-token"},
        }
        response_1 = dict(basic_response)
        response_1["access_token"] = "test-access-token-1"
        response_2 = dict(basic_response)
        response_2["access_token"] = "test-access-token-2"
        response_3 = dict(basic_response)
        response_3["access_token"] = "test-access-token-3"

        rm.put(
            "https://api.pinterest.com/v3/oauth/access_token/",
            [{"json": response_1}, {"json": response_2}, {"json": response_3}],
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

        from scripts.refresh_example import main  # import here to see monkeypatches

        with mock.patch("builtins.open") as mock_open:
            with mock.patch.dict("os.environ", self.mock_os_environ, clear=True):
                mock_open.side_effect = FileNotFoundError  # no access_token.json file
                with self.mock_redirect():
                    main()  # run refresh_example

        mock_sleep.assert_has_calls(
            [mock.call(1), mock.call(1)]
        )  # check calls to time.sleep()

        # verify expected values printed:
        #   one refresh token and three different access tokens
        # echo -n test-refresh-token | shasum -a 256
        mock_print.assert_any_call(
            "hashed refresh token: "
            + "0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde"
        )
        # echo -n test-access-token-1 | shasum -a 256
        mock_print.assert_any_call(
            "hashed access token: "
            + "74e67193d034054f052777eb0b06d0d7fe72016282e2259d466afd6e9f8cc76a"
        )
        # echo -n test-access-token-2 | shasum -a 256
        mock_print.assert_any_call(
            "hashed access token: "
            + "53f55e6fc30e86f042340fe6deec5b3ab5d5d6da11e3e697d41c46143a9cbc2d"
        )
        # echo -n test-access-token-3 | shasum -a 256
        mock_print.assert_any_call(
            "hashed access token: "
            + "f7bba4838772249663c5967b48659745d782ad13bc3abc4a39580eda154ceb97"
        )
