import base64
import hashlib
import json
import os
import pathlib

import requests

from api_common import ApiCommon
from oauth_scope import Scope
from user_auth import get_auth_code


class AccessToken(ApiCommon):
    def __init__(self, api_config, name=None):
        if name:
            self.name = name
        else:
            self.name = "access_token"

        self.api_config = api_config
        self.path = pathlib.Path(api_config.oauth_token_dir) / (self.name + ".json")

        # use the recommended authorization approach
        auth = api_config.app_id + ":" + api_config.app_secret
        b64auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        self.auth_headers = {"Authorization": "Basic " + b64auth}

    def fetch(self, scopes=None, refreshable=True):
        """
        This method tries to make it as easy as possible for a developer
        to start using an OAuth access token. It fetches the access token
        by trying all supported methods, in this order:
           1. Get from the process environment variable that is the UPPER CASE
              version of the self.name attribute. This method is intended as
              a quick hack for developers.
           2. Read the access_token and (if available) the refresh_token from
              the file at the path specified by joining the configured
              OAuth token directory, the self.name attribute, and the '.json'
              file extension.
           3. Execute the OAuth 2.0 request flow using the default browser
              and local redirect.
        """
        try:
            self.from_environment()
            return
        except Exception:
            print(f"reading {self.name} from environment failed, trying read")

        try:
            self.read()
            return
        except Exception:
            print(f"reading {self.name} failed, trying oauth")

        self.oauth(scopes=scopes, refreshable=refreshable)

    def from_environment(self):
        """
        Easiest path for using an access token: get it from the
        process environment. Note that the environment variable name
        is the UPPER CASE of the self.name instance attribute.
        """
        self.access_token = os.environ[self.name.upper()]
        self.refresh_token = None

    def read(self):
        """
        Get the access token from the file at self.path.
        """
        with open(self.path, "r") as jsonfile:
            data = json.load(jsonfile)
            self.name = data.get("name") or "access_token"
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            self.scopes = data.get("scopes")
        print(f"read {self.name} from {self.path}")

    def write(self):
        """
        Store the access token in the file at self.path.
        """
        with open(self.path, "w") as jsonfile:
            # make credential-bearing file as secure as possible
            if "chmod" in dir(os):
                os.chmod(jsonfile.fileno(), 0o600)
            # write the information to the file
            json.dump(
                {
                    "name": self.name,
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "scopes": self.scopes,
                },
                jsonfile,
                indent=2,
            )

    def header(self, headers={}):
        headers["Authorization"] = "Bearer " + self.access_token
        return headers

    def hashed(self):
        """
        Print the access token in a human-readable format that does not reveal
        the actual access credential. The purpose of this method is for a developer
        to verify that the access token has changed after a refresh.
        """
        return hashlib.sha256(self.access_token.encode()).hexdigest()

    def hashed_refresh_token(self):
        """
        Print the refresh token in a human-readable format that does not reveal
        the actual access credential. The purpose of this method is for a developer
        to verify when the refresh token changes.
        """
        if not self.refresh_token:
            raise RuntimeError("AccessToken does not have a refresh token")
        return hashlib.sha256(self.refresh_token.encode()).hexdigest()

    def oauth(self, scopes=None, refreshable=True):
        """
        Execute the OAuth 2.0 process for obtaining an access token.
        For more information, see IETF RFC 6749: https://tools.ietf.org/html/rfc6749
        and https://developers.pinterest.com/docs/getting-started/authentication/

        For v5, scopes are required and tokens must be refreshable.
        """
        if not scopes:
            scopes = [Scope.READ_USERS, Scope.READ_PINS, Scope.READ_BOARDS]
            print(
                "v5 requires scopes for OAuth. setting to default: "
                f"{','.join(list(map(lambda scope: scope.value, scopes)))}"
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

    def refresh(self, continuous=False):
        print(f"refreshing {self.name}...")
        post_data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        if continuous:
            post_data["refresh_on"] = True
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
        # save refresh token if it was also refreshed
        if "refresh_token" in unpacked:
            self.refresh_token = unpacked["refresh_token"]
