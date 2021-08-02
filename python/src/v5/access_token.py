import requests

from access_token_common import AccessTokenCommon
from user_auth import get_auth_code
from v5.oauth_scope import Scope


class AccessToken(AccessTokenCommon):
    def __init__(self, api_config, name=None):
        super().__init__(api_config, name)

    def oauth(self, scopes=None, refreshable=True):
        """
        Execute the OAuth 2.0 process for obtaining an access token.
        For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
        and https://developers.pinterest.com/docs/v5/#tag/oauth

        For v5, scopes are required and tokens must be refreshable.
        """
        if not scopes:
            scopes = [Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS]
            print(
                "v5 requires scopes for OAuth. "
                "setting to default: READ_USERS,READ_PINS,READ_BOARDS"
            )

        if not refreshable:
            raise ValueError(
                "Pinterest API v5 only provides refreshable OAuth access tokens"
            )

        print("getting auth_code...")
        auth_code = get_auth_code(
            self.api_config, scopes=scopes, refreshable=refreshable
        )
        print(f"exchanging auth_code for {self.name}...")
        self.exchange_auth_code(auth_code)

    def exchange_auth_code(self, auth_code):
        """
        Call the Pinterest API to exchange the auth_code (obtained by
        a redirect from the browser) for the access_token and (if requested)
        refresh_token.
        """
        post_data = {
            "code": auth_code,
            "redirect_uri": self.api_config.redirect_uri,
            "grant_type": "authorization_code",
        }
        if self.api_config.verbosity >= 2:
            print("POST", self.api_config.api_uri + "/v5/oauth/token")
            if self.api_config.verbosity >= 3:
                self.api_config.credentials_warning()
                print(post_data)
        response = requests.post(
            self.api_config.api_uri + "/v5/oauth/token",
            headers=self.auth_headers,
            data=post_data,
        )
        unpacked = self.unpack(response)

        print("scope: " + unpacked["scope"])
        self.access_token = unpacked["access_token"]
        self.refresh_token = unpacked["refresh_token"]
        self.scopes = unpacked["scope"]

    def refresh(self):
        print(f"refreshing {self.name}...")
        post_data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        if self.api_config.verbosity >= 2:
            print("POST", self.api_config.api_uri + "/v5/oauth/token")
            if self.api_config.verbosity >= 3:
                self.api_config.credentials_warning()
                print(post_data)
        response = requests.post(
            self.api_config.api_uri + "/v5/oauth/token",
            headers=self.auth_headers,
            data=post_data,
        )
        unpacked = self.unpack(response)
        self.access_token = unpacked["access_token"]
