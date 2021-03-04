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

2. Pick one of the language directories (currently just bash and python) and follow the directions in the README file in the directory.

## OAuth Authentication

Access to Pinterest APIs via User Authorization requires following a flow based on [OAuth 2.0](https://tools.ietf.org/html/rfc6749). For details regarding OAuth, please reference our [developer docs](https://developers.pinterest.com/docs/redoc/#section/User-Authorization). The code in this repo demonstrates how to initiate the flow by starting a browser, and then handling the OAuth redirect to the development machine (localhost). The Pinterest API requires using a secure method for the redirect (https), which is the reason why it's necessary to create the SSL/TLS certificate for localhost.

## Security Notes

* Best development practice is to keep authentication credentials (like your app secret and certificate key) out of your code.
* The recommended locations for your credentials (`common/scripts/api_app_credentials`) and certificates (`common/certs`) are listed in the `.gitignore` file to help avoid checking this material into a git repo.
* To disable the mkcert root certificate, you can run `mkcert -uninstall` and then reenable it later with `mkcert -install`.
* You're safe from abuse after running `mkcert -uninstall`, but to do a deeper cleaning you can run `rm -rf "$(mkcert -CAROOT)"` and also remove the certificate from your computer's trust store (e.g. using the Keychain Access app on MacOS).

## Repository Layout

* The `common` directory stores code and files that work with all of the language-specific directories.
* Each language-specific directory is independent of the others:
  * `bash`: shell scripts
  * `python`: structured python code and demonstration scripts
  * More languages are on the way. We're considering providing examples in nodejs/JavaScript, ruby, and Java.
* Each language-specific directory (e.g. `python` or `bash`) has one or more of these subdirectories:
  * `scripts` are executable files that demonstrate one or more use cases.
  * `src` contains code that is used by the scripts and that you can incorporate into your own applications
  * `tests` contains unit and integration tests.
