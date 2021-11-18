# pinterest/api-quickstart

Code that makes it easy to get started with the Pinterest API.

## Purpose

This repository has code that is intended to provide a quick start for working with the [Pinterest API v5](https://developers.pinterest.com/docs/api/v5/), and also supports [Pinterest API v3](https://developers.pinterest.com/docs/redoc/). There is currently python code that implements a number of use cases, JavaScript (nodejs) code with essentially the same functionality, and a bash script that demonstrates the OAuth authentication and authorization flow. Over time, we plan to add more demonstrations of API functionality and additional languages -- likely Ruby and maybe Go or PHP.

## Quick Start

1. Set up the environment with your credentials (app ID and secret). This configuration works with the code in all of the language-specific directories.

   * Get an application ID and secret by hitting the "Connect app" button at [https://developers.pinterest.com/apps/](https://developers.pinterest.com/apps/). You may first need to follow the steps required to [request trial access](https://developers.pinterest.com/docs/api/v5/#section/Requesting-Trial-Access) to the Pinterest API. You can also find step-by-step instructions on the [Glitch-based tutorial](https://pinterest-oauth-tutorial.glitch.me/).
   * Once your app is connected, hit the Manage button for the app on [https://developers.pinterest.com/apps/](https://developers.pinterest.com/apps/) to see your App id and App secret key. (Click the Show key button to see the App secret key.)
   * Put your App ID and App secret key in an environment script file.
     ```
     $ cd common/scripts
     $ cp api_app_credentials.template api_app_credentials
     # edit api_app_credentials and enter your app id and secret in the specified locations
     $ cd ../..
     ```
   * Configure the OAuth2 redirect URI required by this code.
     1. Click on the Manage button for your application at [https://developers.pinterest.com/apps/](https://developers.pinterest.com/apps/).
     2. In the box labeled "Redirect link," enter `http://localhost:8085/`.
     3. Hit the return (enter) key or the Add button to save redirect URI (link).
   * Run the environment set-up script and verify the results.
     ```
     $ . ./common/scripts/api_env
     $ env | grep PINTEREST_APP
     PINTEREST_APP_ID=<number>
     PINTEREST_APP_SECRET=<string>
     ```

2. Pick one of the language directories (currently bash, nodejs and python) and follow the directions in the README file in the directory:
   * [NodeJS README](./nodejs/README.md)
     ```
     cd ./nodejs
     ```
   * [Python README](./python/README.md)
     ```
     cd ./python
     ```
   * [Bash README](./bash/README.md)
     ```
     cd ./bash
     ```

## OAuth 2.0 Authorization

Access to Pinterest APIs via User Authorization requires following a flow based on [OAuth 2.0](https://tools.ietf.org/html/rfc6749). To learn about how to use OAuth 2.0 with the Pinterest API, check out the [Glitch-based tutorial](https://pinterest-oauth-tutorial.glitch.me/). For details regarding OAuth, please refer to our [v5 developer docs](https://developers.pinterest.com/docs/api/v5/#tag/Authentication) or [v3 developer docs](https://developers.pinterest.com/docs/redoc/#section/User-Authorization). The code in this repo demonstrates how to initiate the flow by starting a browser, and then handling the OAuth redirect to the development machine (localhost). The browser is used to obtain an authorization code, and then the code invoked by the redirect exchanges the authorization code for an access token.

An access token is used to authenticate most API calls. In general, access tokens are valid for relatively long periods of time, in order to avoid asking users to go through the OAuth flow too often. When an access token expires, it is possible to refresh the token -- a capability that the code in this repo also demonstrates.

Like users, most developers do not want to have to go through the OAuth flow too often. So, the python code supports (and soon, other languages will support) two methods for storing OAuth access token:
* Storing the access token to a JSON-encoded file. The default path in this repo for storing access tokens is `common/oauth_tokens/access_token.json`. To generate this file, use the language-specific `get_access_token` script with the `-w` argument. You can also use the `-a` argument to specify the name of the token, which is the same as the name of the JSON file. For example, set up the python environment and then run `python/scripts/get_access_token.py -w -a my_access_token -s READ_USERS`. The contents of this file can be as simple as this JSON: `{"access_token": "<access token retrieved from OAuth flow>"}`. The complete set of JSON object keys are:
   * `access_token`: The access token returned by the OAuth flow. [required]
   * `name`: A textual description of the access token. (e.g. "API test account #2")
   * `refresh_token`: The refresh token returned by the OAuth flow.
   * `scopes`: The OAuth scopes associated with the token
* Storing the access token in an environment variable. The default environment variable is simply `ACCESS_TOKEN`, so running the command `export ACCESS_TOKEN=<access_token_retrieved_via_oauth>` will work in most situations. This method for specifying an access token is intended to be the easiest, fastest way to use an externally-generated access token with the code in this repo.

The precedence order in this repo for obtaining an access token is: environment, file, execute the OAuth 2.0 flow.

Code that implements OAuth is available for each language in this repo. The location of the code is as follows.
   * One bash script for each version of the Pinterest API provide complete examples: [bash/scripts/v3/get_access_token.sh](bash/scripts/v3/get_access_token.sh) and [bash/scripts/v5/get_access_token.sh](bash/scripts/v5/get_access_token.sh).
   * In python, the version-independent code in [python/src/user_auth.py](python/src/user_auth.py) opens a browser and handles the redirect to obtain an authorization code. The version-dependent code to exchange the authorization code for an access token is in [python/src/v3/access_token.py](python/src/v3/access_token.py) and [python/src/v5/access_token.py](python/src/v5/access_token.py). These two files also implement access token refresh.
   * In JavaScript, the version-independent code in [nodejs/src/user_auth.js](nodejs/src/user_auth.js) opens a browser and handles the redirect to obtain an authorization code. The version-dependent code to exchange the authorization code for an access token is in [nodejs/src/v3/access_token.js](nodejs/src/v3/access_token.js) and [nodejs/src/v5/access_token.js](nodejs/src/v5/access_token.js). These two files also implement access token refresh.

## Security Notes

* Best development practice is to keep authentication credentials (like your app secret and OAuth access tokens) out of code.
* When using a JSON-encoded file to specify an access token, use a secure file mode when possible. For example: `chmod 600 common/oauth_tokens/*`
* When specifying credentials in environment variables, export it from a script file instead of on the shell command line. (Commands -- along with the clear text credentials -- are often stored in history and log files.)
* The recommended locations for your credentials (`common/scripts/api_app_credentials`), and access tokens (`common/oauth_tokens`) are listed in the `.gitignore` file to help avoid checking this material into a git repo.
* Specifying a high level of logging verbosity may print credentials in clear text. This data is useful for local debugging, but should be protected -- not transmitted via email or other insecure kinds of communication.

## Repository Layout

* The `common` directory stores code and files that work with all of the language-specific directories.
* Each language-specific directory is independent of the others:
  * `bash`: shell scripts
  * `nodejs`: JavaScript code and demonstration scripts intended to be run with Node.js
  * `python`: structured python code and demonstration scripts. Since the python code is implemented first, python typically has the most functionality.
  * More languages are on the way. We're considering providing examples in ruby and Java.
* Each language-specific directory (e.g. `python` or `bash`) has one or more of these subdirectories:
  * `scripts` are executable files that demonstrate one or more use cases.
  * `src` contains code that is used by the scripts and that you can incorporate into your own applications.
  * `tests` contains unit and integration tests.
* Code that is specific to versions of the Pinterest API is in subdirectories of `src` (in the case of python and nodejs) or `scripts` (in the case of bash). The two versions supported by this quickstart are v3 and v5.

## Other Resources

  * [Pinterest Developers](https://developers.pinterest.com/)
  * [Pinterest OAuth 2.0 Tutorial](https://pinterest-oauth-tutorial.glitch.me/)
  * [Pinterest Engineering Blog](https://medium.com/pinterest-engineering)
  * The [pinterest/api-description](https://github.com/pinterest/api-description) repo on GitHub contains [OpenAPI](https://www.openapis.org/) descriptions for Pinterest's REST API.
