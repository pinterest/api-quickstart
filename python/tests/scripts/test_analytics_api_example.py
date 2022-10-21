import json
from unittest import mock
from unittest.mock import call

import requests_mock
from integration_mocks import IntegrationMocks


class AnalyticsApiExampleTest(IntegrationMocks):
    """
    Test all of the different stages of the analytics API example.
    """

    report_url_filename = "here_is_the_filename.txt"  # filename in the report url
    download_filename = "test_report_file.txt"  # filename "entered" for download
    report_url = (
        f"https://test-report-url/x-y-z/{report_url_filename}?long-identifier-string"
    )

    def mock_input(self, prompt):
        print("mock_input", prompt)
        self.input_calls += 1
        if prompt == "[1] ":  # Please select an advertisers between 1 and N
            return "2"  # select the second advertiser
        if (
            prompt == f"[{self.report_url_filename}] "
        ):  # Please enter a file name for the report
            return self.download_filename  # check the retrieved filename and change it
        raise ValueError(f"unexpected input prompt: {prompt}")

    @requests_mock.Mocker()
    def test_analytics_api_example(self, rm):
        # request from AsyncReport.request_report
        rm.post(
            "https://api.pinterest.com/v5/ad_accounts/" "adv_2_id/reports",
            json={"report_status": "IN_PROGRESS", "token": "test-report-token"},
        )

        # request from User.get
        rm.get(
            "https://api.pinterest.com/v5/user_account",
            json={
                "account_type": "BUSINESS",
                "profile_image": "test_profile_image",
                "website_url": "test_website_url",
                "username": "test user name",
            },
        )
        # request from Advertisers.get
        rm.get(
            "https://api.pinterest.com/v5/ad_accounts",
            json={
                "items": [
                    {"name": "test advertiser 1", "id": "adv_1_id"},
                    {"name": "test advertiser 2", "id": "adv_2_id"},
                    {"name": "test advertiser 3", "id": "adv_3_id"},
                ]
            },
        )

        # request from AsyncReport.poll_report
        rm.get(
            "https://api.pinterest.com/v5/ad_accounts/"
            "adv_2_id/reports"
            "?token=test-report-token",
            json={"report_status": "FINISHED", "url": self.report_url},
        )

        # request from generic_requests.download_file
        first_chunk = (
            "a" * 4096
        )  # 4096 = chunk size specified in generic_requests.download_file
        second_chunk = "b" * 8
        rm.get(self.report_url, text=(first_chunk + second_chunk))

        # import main here to see monkeypatches
        from scripts.analytics_api_example import main

        access_token_dict = {
            "name": "access_token_from_file",
            "access_token": "test access token from json",
            "refresh_token": "test refresh token from json",
        }

        # Mock the access_token.json file in order to avoid having to
        # do the redirect through a webserver running on localhost,
        # which is tested in other scripts.
        mock_file = mock.MagicMock()
        mock_file.read.return_value = json.dumps(access_token_dict)
        # Mocking __enter__ provides for the open call in a context manager.
        mock_file.__enter__.return_value = mock_file

        self.input_calls = 0

        with mock.patch("builtins.open") as mock_open:
            with mock.patch.dict("os.environ", self.mock_os_environ, clear=True):
                mock_open.return_value = mock_file
                main()  # run analytics_api_example
                mock_open.assert_any_call(self.download_filename, "wb")

        self.assertEqual(self.input_calls, 2)
        mock_file.write.assert_has_calls(
            [call(first_chunk.encode("ascii")), call(second_chunk.encode("ascii"))]
        )
