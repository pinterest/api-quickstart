import json
import unittest

import mock

from src.access_token_common import AccessTokenCommon


class AccessTokenCommonTest(unittest.TestCase):

    mock_os_environ_access_token = {"ACCESS_TOKEN_FROM_ENV": "access token 42"}

    @mock.patch.dict("os.environ", mock_os_environ_access_token, clear=True)
    def test_access_token_from_environment(self):
        mock_api_config = mock.Mock()
        mock_api_config.app_id = "test-app-id"
        mock_api_config.app_secret = "test-app-secret"
        mock_api_config.oauth_token_dir = "test-token-dir"

        # The name of the access token is converted to upper case to find
        # it in the process environment.
        access_token = AccessTokenCommon(mock_api_config, name="access_token_from_env")
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

        access_token = AccessTokenCommon(mock_api_config, name="access_token_from_file")
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
