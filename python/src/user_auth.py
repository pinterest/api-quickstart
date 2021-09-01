import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from webbrowser import open_new


class HTTPServerHandler(BaseHTTPRequestHandler):
    """
    HTTP Server callback to handle Pinterest OAuth redirect with auth_code
    """

    def __init__(self, request, address, server, api_config, oauth_state):
        self.api_config = api_config
        self.oauth_state = oauth_state
        super().__init__(request, address, server)

    # override log_message to prevent logging the auth_code to the console
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.api_config.verbosity >= 3:
            self.api_config.credentials_warning()
            print("Redirect request path:", self.path)
        # redirect to the landing_uri
        self.send_response(301)
        self.send_header("Location", self.api_config.landing_uri)
        self.end_headers()

        # Get the state and auth_code from the path of the redirect URI.
        # Start by parsing the URL path.
        parsed_query = parse_qs(urlparse(self.path).query)

        # verify state
        state_params = parsed_query.get("state")
        received_oauth_state = None
        if isinstance(state_params, (list)):
            received_oauth_state = state_params[0]
        if self.oauth_state != received_oauth_state:
            raise RuntimeError("Received OAuth state does not match sent state")

        # save the authorization code
        code_params = parsed_query.get("code")
        if isinstance(code_params, (list)):
            self.server.auth_code = code_params[0]
        else:
            raise RuntimeError("OAuth redirect does not have an auth code")


def get_auth_code(api_config, scopes=None, refreshable=True):
    """
    Executes the process required to obtain an OAuth user authentication code.
      1. Use the default web browser to send a request to the /oauth endpoint.
      2. Start a web (https) server on localhost to get the auth_code.
      3. Wait until the browser executes the authentication process and sends
         the code via the redirect.
    """

    access_uri = (
        api_config.oauth_uri
        + "/oauth/"
        + "?consumer_id="
        + api_config.app_id
        + "&redirect_uri="
        + api_config.redirect_uri
        + "&response_type=code"
        + "&refreshable="
        + str(refreshable)
    )

    if scopes:
        access_uri = (
            access_uri
            + "&scope="
            + ",".join(list(map(lambda scope: scope.value, scopes)))
        )

    # The OAuth state parameter is intended to prevent cross-site scripting
    # exploits. The state should incorporate cryptographically secure randomness
    # so create it with the secrets module, which is intended for this purpose.
    # oauth_state goes at the end of access_uri to make it easier to read
    # and to debug the access URI.
    oauth_state = secrets.token_hex()
    access_uri += f"&state={oauth_state}"

    """
    Open a web browser. There's a race condition between the browser
    doing the redirect and the handle_request call below. It is very
    unlikely that the browser will start and get human input before
    the localhost https server can start.
    """
    if api_config.verbosity >= 3:
        print("OAuth URI:", access_uri)
    open_new(access_uri)

    httpServer = HTTPServer(
        ("localhost", api_config.port),
        lambda request, address, server: HTTPServerHandler(
            request, address, server, api_config, oauth_state
        ),
    )

    # This function will block until it receives a request
    try:
        httpServer.handle_request()
    except KeyboardInterrupt:
        """
        This flow will typically be interrupted by the developer if the
        OAuth did not work in the browser. For details, see the documentation:
         https://developers.pinterest.com/docs/api/v5/#tag/Authentication
         https://developers.pinterest.com/docs/redoc/#section/User-Authorization/Start-the-OAuth-flow-%28explicit-server-side%29
        """  # noqa: E501 because the long URL is okay
        sys.exit("\nSorry that the OAuth redirect didn't work out. :-/")

    # Return the access token
    return httpServer.auth_code
