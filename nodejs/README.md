# Node.js Quickstart

JavaScript code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring
your application ID, application secret, and https certificates.

2. From the top of this repo, change your working directory to this directory: `cd nodejs`

3. Install [nodejs](https://nodejs.org/en/download/).

4. Install the node packages.

   ```
   $ npm install
   ```

5. Set up the shell environment.

   ```
   $ . ../common/scripts/api_env
   ```

6. Run the simplest sample script.

   ```
   $ ./scripts/get_access_token.js
   ```

## Additional Functionality

After running the Quick Start, you should be able to run any of the use cases in the scripts directory:
  * `get_access_token.js`: Quick start code that demonstrates the OAuth 2.0 flow and tests the authentication by reading the user profile using the `/v3/users/{user}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_user_handler_GET).
  * `refresh_example.js`: Demonstrates how to refresh an access token.
  * `get_businesses.js`: Reads the `/v3/users/{user}/businesses/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_linked_business_accounts_GET). This script will generate a 400 error if your application does not have access to the `read_advertisers` scope. To see any data, the authorized account needs to have linked business acounts.

In every new shell, you'll need to configure the environment.

```
$ cd nodejs # from the top of this repository
$ . ../common/scripts/api_env
```
