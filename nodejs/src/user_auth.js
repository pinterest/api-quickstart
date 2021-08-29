import http from 'http';
import open from 'open';
import { v4 as uuidv4 } from 'uuid';
import url from 'url';

/**
 * Executes the process required to obtain an OAuth user authentication code.
 *   1. Use the default web browser to send a request to the /oauth endpoint.
 *   2. Start a web (https) server on localhost to get the auth_code.
 *   3. Wait until the browser executes the authentication process and sends
 *      the code via the redirect.
 */
export default async function get_auth_code(
  api_config, { scopes = null, refreshable = true }) {
  const oauth_state = uuidv4(); // uuidv4 is cryptographically secure

  const auth_code = new Promise((resolve, reject) => {
    const sockets = []; // tracks the sockets connected to the server

    // http is required to implement the Pinterest API redirect
    const server = http.createServer(function(req, res) {
      if (api_config.verbosity >= 3) {
        api_config.credentials_warning();
        console.log('Redirect request path:', req.url);
      }
      res.writeHead(301, {
        Location: api_config.landing_uri
      });
      res.end(function() {
        // Only one response is expected or desired, so close down the server.
        server.close();
        // For the server to complete the termination process, need to
        // terminate the sockets cleanly.
        sockets.forEach(function(socket) {
          // First call socket.end to send a FIN, then destroy the socket.
          socket.end(function() { socket.destroy(); });
        });

        // Parse the url. Instead of reconstructing the base from req,
        // just provide example.com as a base.
        const params = new url.URL(req.url, 'http://example.com/').searchParams;
        if (params.get('state') !== oauth_state) {
          // verify that the returned state is as expected
          reject(new Error('Received OAuth state does not match sent state'));
        }
        resolve(params.get('code'));
      });
    });

    // Capture the open sockets so that the server can be terminated completely.
    server.on('connection', function(socket) { sockets.push(socket); });

    // Start listening on the requested port.
    server.listen(api_config.port);
  });

  let access_uri = `\
${api_config.oauth_uri}/oauth/\
?consumer_id=${api_config.app_id}\
&redirect_uri=${api_config.redirect_uri}\
&response_type=code\
&refreshable=${refreshable.toString()}\
`;

  if (scopes) {
    access_uri += `&scope=${scopes.map(s => s.value).join(',')}`;
  }

  // The OAuth state parameter is intended to prevent cross-site scripting
  // exploits. The state should incorporate cryptographically secure randomness,
  // which should be satisfied by the uuid.v4 function.
  // oauth_state goes at the end of access_uri to make it easier to read
  // and to debug the access URI.
  access_uri += `&state=${oauth_state}`;

  // open the default browser for user interaction
  if (api_config.verbosity >= 3) {
    console.log('OAuth URI:', access_uri);
  }
  open(access_uri);

  // Returns the promise that will eventually resolve into the auth_code.
  return auth_code;
}
