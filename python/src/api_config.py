import os # for environment variables
import sys # for sys.path.append

from os.path import dirname, abspath, join

# Construct the redirect_uri for the OAuth process. The REDIRECT_URI must
# be literally the same as configured at https://developers.pinterest.com/manage/.
# The port is fixed for now. It would be better to configure a selection
# of ports that could be used in case some other service is listening on
# the hard-coded port.
DEFAULT_PORT = 8085
DEFAULT_REDIRECT_URI = 'https://localhost:' + str(DEFAULT_PORT) + '/'
DEFAULT_API_URI = 'https://api.pinterest.com'
DEFAULT_API_VERSION = 'v3'
DEFAULT_OAUTH_URI = 'https://www.pinterest.com'
DEFAULT_LANDING_URI = 'https://developers.pinterest.com/manage/'
DEFAULT_KEY_FILE = 'localhost-key.pem'
DEFAULT_CERT_FILE = 'localhost.pem'
# OAuth tokens are in the current directory by default
DEFAULT_OAUTH_TOKEN_DIR = '.'

class RateLimitException(Exception):
    """Raised when API emits a HTTP 429 Too Many Requests Error"""
    pass

class SpamException(Exception):
    """Raised when API emits a HTTP 429 due to a spam issue"""

class ApiConfig:
    def __init__(self):
        # Get Pinterest application ID and secret from the OS environment.
        # It is best practice not to store credentials in code.
        self.app_id = os.environ['PINTEREST_APP_ID']
        self.app_secret = os.environ['PINTEREST_APP_SECRET']

        # might want to get these from the environment in the future
        self.port = DEFAULT_PORT
        self.redirect_uri = DEFAULT_REDIRECT_URI
        self.landing_uri = os.environ.get('REDIRECT_LANDING_URI') or DEFAULT_LANDING_URI + self.app_id

        # locations of credentials in the file system
        self.https_key_file = os.environ.get('HTTPS_KEY_FILE') or DEFAULT_KEY_FILE
        self.https_cert_file = os.environ.get('HTTPS_CERT_FILE') or DEFAULT_CERT_FILE
        self.oauth_token_dir = os.environ.get('PINTEREST_OAUTH_TOKEN_DIR') or DEFAULT_OAUTH_TOKEN_DIR

        # swizzle oauth and api hosts, based on environment
        self.oauth_uri = os.environ.get('PINTEREST_OAUTH_URI') or DEFAULT_OAUTH_URI
        self.api_uri = os.environ.get('PINTEREST_API_URI') or DEFAULT_API_URI
        self.version = os.environ.get('PINTEREST_API_VERSION') or DEFAULT_API_VERSION

        # default level of verbosity, probably should switch to logging
        self.verbosity = 1

        # set up to load the code modules for this version of the API
        sys.path.append(abspath(join(dirname(__file__), self.version)))
