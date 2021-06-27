import http from 'http'
import fs from 'fs'
import open from 'open'

export default async function get_auth_code(
  api_config, {scopes = null, refreshable = true}) {
  const auth_code = new Promise((resolve, reject) => {

    const sockets = []; // tracks the sockets connected to the server

    // http is required to implement the Pinterest API redirect
    const server = http.createServer(function (req, res) {
      res.writeHead(301, {
        'Location': api_config.landing_uri
      })
      res.end(function () {
        // Only one response is expected or desired, so close down the server.
        server.close();
        // For the server to complete the termination process, need to
        // terminate the sockets cleanly.
        sockets.forEach(function(socket) {
          // First call socket.end to send a FIN, then destroy the socket.
          socket.end(function () { socket.destroy(); });
        });
        // Finally, return the code to the awaiting caller.
        resolve(req.url.split('=')[1]);
      });
    });

    // Capture the open sockets so that the server can be terminated completely.
    server.on('connection', function (socket) { sockets.push(socket); });

    // Start listening on the requested port.
    server.listen(api_config.port);
  });

  var access_uri = (api_config.oauth_uri + '/oauth/' +
                    '?consumer_id=' + api_config.app_id +
                    '&redirect_uri=' + api_config.redirect_uri +
                    '&response_type=code' +
                    '&refreshable=' + refreshable.toString());

  if (scopes) {
    access_uri = access_uri + '&scope=' + scopes.map(s => s.value).join(',');
  }

  // open the default browser for user interaction
  open(access_uri);

  // Returns the promise that will eventually resolve into the auth_code.
  return auth_code;
}
