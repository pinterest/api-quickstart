import os  # for environment variables
import sys  # for sys.path.append
from os.path import abspath, dirname, join

# Construct the redirect_uri for the OAuth process. The REDIRECT_URI must
# be literally the same as configured at https://developers.pinterest.com/apps/.
# The port is fixed for now. It would be better to configure a selection
# of ports that could be used in case some other service is listening on
# the hard-coded port.
DEFAULT_PORT = 8085
DEFAULT_REDIRECT_URI = "http://localhost:" + str(DEFAULT_PORT) + "/"
DEFAULT_API_URI = "https://api.pinterest.com"
DEFAULT_API_VERSION = "v5"
DEFAULT_OAUTH_URI = "https://www.pinterest.com"
DEFAULT_LANDING_URI = "https://developers.pinterest.com/apps/"
# OAuth tokens are in the current directory by default
DEFAULT_OAUTH_TOKEN_DIR = "."


class ApiConfig:
    def __init__(self, verbosity=2, version=None):
        # Set logging output (verbosity) level
        self.verbosity = verbosity

        # Get Pinterest API version from the command line, environment,
        # or above default.
        if version:
            self.version = "v" + str(version)
        else:
            self.version = (
                os.environ.get("PINTEREST_API_VERSION") or DEFAULT_API_VERSION
            )

        # get the required application ID and secret from the environment,
        # based on the version
        self.get_application_id()

        # might want to get these from the environment in the future
        self.port = DEFAULT_PORT
        self.redirect_uri = DEFAULT_REDIRECT_URI
        self.landing_uri = (
            os.environ.get("REDIRECT_LANDING_URI") or DEFAULT_LANDING_URI + self.app_id
        )

        # locations of credentials in the file system
        self.oauth_token_dir = (
            os.environ.get("PINTEREST_OAUTH_TOKEN_DIR") or DEFAULT_OAUTH_TOKEN_DIR
        )

        # swizzle oauth and api hosts, based on environment
        self.oauth_uri = os.environ.get("PINTEREST_OAUTH_URI") or DEFAULT_OAUTH_URI
        self.api_uri = os.environ.get("PINTEREST_API_URI") or DEFAULT_API_URI

        # set up to load the code modules for this version of the API
        sys.path.append(abspath(join(dirname(__file__), self.version)))

    def get_application_id(self):
        """
        Get Pinterest application ID and secret from the OS environment.
        It is best practice not to store credentials in code nor to provide
        credentials on a shell command line.

        First, try the version-specific environment variables like
        PINTEREST_V3_APP_ID and PINTEREST_V3_APP_SECRET.
        Then, try the non-version-specific environment variables like
        PINTEREST_V5_APP_ID and PINTEREST_V5_APP_SECRET.

        Exit with error code 1 (argument error) if the application id and secret
        can not be found in the environment.
        """
        env_app_id = f"PINTEREST_{self.version}_APP_ID".upper()
        env_app_secret = f"PINTEREST_{self.version}_APP_SECRET".upper()
        app_id = os.environ.get(env_app_id)
        app_secret = os.environ.get(env_app_secret)
        if app_id and app_secret:
            # version-specific application ID and secret override
            # non-version-specific credentials
            self.app_id = app_id
            self.app_secret = app_secret
        else:
            # try non-version-specific application ID and secret
            env_app_id = "PINTEREST_APP_ID"
            env_app_secret = "PINTEREST_APP_SECRET"
            self.app_id = os.environ.get(env_app_id)
            self.app_secret = os.environ.get(env_app_secret)

        if self.app_id and self.app_secret:
            if self.verbosity >= 2:
                print(
                    f"Using application ID and secret "
                    f"from {env_app_id} and {env_app_secret}."
                )
            return

        print(f"{env_app_id} and {env_app_secret} must be set in the environment.")
        exit(1)

    def credentials_warning(self):
        print("WARNING: This log has clear text credentials that need to be protected.")
