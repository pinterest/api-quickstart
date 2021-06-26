import ssl # for implementing the https scheme for the redirect URI
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from webbrowser import open_new

class HTTPServerHandler(BaseHTTPRequestHandler):
    """
    HTTP Server callback to handle Pinterest OAuth redirect with auth_code
    """
    def __init__(self, request, address, server, landing_uri):
        self.landing_uri = landing_uri
        super().__init__(request, address, server)

    # override log_message to prevent logging the auth_code to the console
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        # redirect the developer to the management page for their app
        self.send_response(301)
        self.send_header('Location', self.landing_uri)
        self.end_headers()
        # get the auth_code from the path of the redirect URI
        if 'code' in self.path:
            self.server.auth_code = self.path.split('=')[1]

def get_auth_code(api_config, scopes=None, refreshable=True):
    """
    Executes the process required to obtain an OAuth user authentication code.
      1. Use the default web browser to send a request to the /oauth endpoint.
      2. Start a web (https) server on localhost to get the auth_code.
      3. Wait until the browser executes the authentication process and sends
         the code via the redirect.
    """

    access_uri = (api_config.oauth_uri + '/oauth/' +
                  '?consumer_id=' + api_config.app_id +
                  '&redirect_uri=' + api_config.redirect_uri +
                  '&response_type=code' +
                  '&refreshable=' + str(refreshable))

    if scopes:
        access_uri = access_uri + '&scope=' + ','.join(list(map(lambda scope: scope.value, scopes)))

    """
    Open a web browser. There's a race condition between the browser
    doing the redirect and the handle_request call below. It is very
    unlikely that the browser will start and get human input before
    the localhost https server can start.
    """
    open_new(access_uri)

    httpServer = HTTPServer(('localhost', api_config.port),
                            lambda request, address, server: HTTPServerHandler(
                                request, address, server, api_config.landing_uri))

    # This function will block until it receives a request
    try:
        httpServer.handle_request()
    except KeyboardInterrupt:
        """
        This flow will typically be interrupted by the developer if the OAuth did not work in the browser.
        For details, see:
         https://developers.pinterest.com/docs/redoc/#section/User-Authorization/Start-the-OAuth-flow-(explicit-server-side)
        """
        sys.exit("\nSorry that the OAuth redirect didn't work out. :-/")

    # Return the access token
    return httpServer.auth_code
