# pinterest-api-quickstart

Code that makes it easy to get started with the Pinterest API.

## Purpose

This repository has code that is intended to provide a quick start for working with the [Pinterest API](https://developers.pinterest.com/docs/redoc/). The current version is really just a first draft. It has some shell (bash) scripts and python code that demonstrate "hello, world" functionality. Over time, we hope to demonstrate a lot more of the API functionality and support a few more languages.

## Quick Start

1. Set up the environment with your credentials (app ID and secret, https://localhost certificates). This configuration works with the code in all of the language-specific directories.

   * Get an application ID and secret by hitting the "Start building" button at [https://developers.pinterest.com/](https://developers.pinterest.com/). Currently, approval from a contact at Pinterest is required to see the application secret. We realize that this process isn't awesome right now, but we're working on it!
   * Put your app ID and secret in an environment script file.
     ```
     $ cd common/scripts
     $ cp api_app_credentials.template api_app_credentials
     # edit api_app_credentials and enter your app id and secret in the specified locations
     $ cd ../..
     ```
   * Configure the redirect URI required by this code.
     1. Click on the name of your application at [https://developers.pinterest.com/manage/](https://developers.pinterest.com/manage/).
     2. In the box labeled "Redirect URIs," enter `https://localhost:8085/`.
     3. Hit the return (enter) key.
     4. Hit the Save button next in the "You have unsaved changes" box that appears after hitting the return (enter) key.
   * Create a certificate so that your browser will trust https://localhost/. This configuration will streamline the OAuth process on your development machine. We recommend installing and using [mkcert](https://github.com/FiloSottile/mkcert) for this purpose.
     ```
     $ mkdir -p common/certs # create the directory
     $ cd common/certs
     $ mkcert -install # if you have not already run this command
     $ mkcert localhost
     $ cd ../..
     ```
   * Run the environment set-up script and verify the results.
     ```
     $ . ./common/scripts/api_env
     $ env | grep PINTEREST_APP
     PINTEREST_APP_ID=<number>
     PINTEREST_APP_SECRET=<string>
     $ env | grep HTTPS
     HTTPS_KEY_FILE=<this directory>/common/scripts/../certs/localhost-key.pem
     HTTPS_CERT_FILE=<this directory>/common/scripts/../certs/localhost.pem
     ```

2. Pick one of the language directories (currently bash, nodejs and python) and follow the directions in the README file in the directory.

## OAuth Authentication

Access to Pinterest APIs via User Authorization requires following a flow based on [OAuth 2.0](https://tools.ietf.org/html/rfc6749). For details regarding OAuth, please reference our [developer docs](https://developers.pinterest.com/docs/redoc/#section/User-Authorization). The code in this repo demonstrates how to initiate the flow by starting a browser, and then handling the OAuth redirect to the development machine (localhost). The browser is used to obtain an authorization code, and then the code invoked by the redirect exchanges the authorization code for an access token. The Pinterest API requires using a secure method for the redirect (https), which is the reason why it's necessary to create the SSL/TLS certificate for localhost.

An access token is used to authenticate most API calls. In general, access tokens are valid for relatively long periods of time, in order to avoid asking users to go through the OAuth flow too often. When an access token expires, it is possible to refresh the token -- a capability that the code in this repo also demonstrates.

Like users, most developers do not want to have to go through the OAuth flow too often. So, the python code supports (and soon, other languages will support) two methods for storing OAuth access token:
* Storing the access token to a JSON-encoded file. The default path in this repo for storing access tokens is `common/oauth_tokens/access_token.json`. To generate this file, use the language-specific `get_access_token` script with the `-w` argument. For example, set up the python environment and then run `python/scripts/get_access_token.py -w`. The contents of this file can be as simple as this JSON: `{"access_token": "<access token retreived from OAuth flow>"}`. The complete set of JSON object keys are:
   * `access_token`: The access token returned by the OAuth flow. [required]
   * `name`: A textual description of the access token. (e.g. "API test account #2")
   * `refresh_token`: The refresh token returned by the OAuth flow.
* Storing the access token in an environment variable. The default environment variable is simply `ACCESS_TOKEN`, so running the command `export ACCESS_TOKEN=<access_token_retrieved_via_oauth>` will work in most situations. This method for specifying an access token is intended to be the easiest, fastest way to use an externally-generated access token with the code in this repo.

The precedence order in this repo for obtaining an access token is: environment, file, execute the OAuth 2.0 flow.

## Security Notes

* Best development practice is to keep authentication credentials (like your app secret, certificate key, and access tokens) out of code.
* When using a JSON-encoded file to specify an access token, use a secure file mode when possible. For example: `chmod 600 common/oauth_tokens/*`
* When specifying credentials in environment variables, export it from a script file instead of on the shell command line. (Commands -- along with the clear text credentials -- are often stored in history and log files.)
* The recommended locations for your credentials (`common/scripts/api_app_credentials`), certificates (`common/certs`), and access tokens (`common/oauth_tokens`) are listed in the `.gitignore` file to help avoid checking this material into a git repo.
* To disable the mkcert root certificate, you can run `mkcert -uninstall` and then reenable it later with `mkcert -install`.
* You're safe from abuse after running `mkcert -uninstall`, but to do a deeper cleaning you can run `rm -rf "$(mkcert -CAROOT)"` and also remove the certificate from your computer's trust store (e.g. using the Keychain Access app on MacOS).

## Repository Layout

* The `common` directory stores code and files that work with all of the language-specific directories.
* Each language-specific directory is independent of the others:
  * `bash`: shell scripts
  * `nodejs`: JavaScript code and demonstration scripts intended to be run with Node.js
  * `python`: structured python code and demonstration scripts
  * More languages are on the way. We're considering providing examples in nodejs/JavaScript, ruby, and Java.
* Each language-specific directory (e.g. `python` or `bash`) has one or more of these subdirectories:
  * `scripts` are executable files that demonstrate one or more use cases.
  * `src` contains code that is used by the scripts and that you can incorporate into your own applications
  * `tests` contains unit and integration tests.
