# Python Quickstart

Python code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring
your application ID, application secret, and https certificates.

2. From the top of this repo, change your working directory to this directory: `cd python`

3. Set up your virtualenv.

   ```
   $ python3 -m venv ./venv/api
   $ . ./venv/api/bin/activate
   $ pip install -r requirements.txt
   ```

4. Set up the shell environment.

   ```
   $ . ../common/scripts/api_env
   ```

5. Run the simplest sample script.

   ```
   $ ./scripts/get_access_token.py
   ```

## Additional Functionality

After running the Quick Start, you should be able to run any of the use cases in the scripts directory:
  * `get_access_token.py`: Quick start code that demonstrates the OAuth 2.0 flow and tests the authentication by reading the user profile using the `/v3/users/{user}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_user_handler_GET). Running this script with the `-w` parameter (`./scripts/get_access_token -w`) stores the access token in `../common/oauth_tokens/access_token.json` for future use.
  * `refresh_example.py`: Demonstrates how to refresh an access token.
  * `get_businesses.py`: Reads the `/v3/users/{user}/businesses/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_linked_business_accounts_GET). This script will generate a 400 error if your application does not have access to the `read_advertisers` scope. To see any data, the authorized account needs to have linked business acounts.
  * `analytics_api_example.py`: Demonstrates how to use the API to generate an asynchronous delivery metrics report using the [request](https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_create_advertiser_delivery_metrics_report_POST) and [get](https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_get_advertiser_delivery_metrics_report_handler_GET) endpoints.
  * `get_pin.py`: Retrieves the information for a specific board with the `/v3/pins/{pin}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pin_GET).
  * `get_board.py`: Retrieves the information for a specific board with the `/v3/boards/{board}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_board_GET).
  * `get_user_pins.py`: Retrieves all of the pins for a user with the `/v3/users/{users}/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pins_handler_GET), using the paging mechanism of the API.
  * `get_user_boards.py`: Retrieves all of the boards for a user with the `/v3/users/{user}/boards/feed/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET), using the paging mechanism of the API.
  * `copy_pin.py`: Demonstration of how to use the `PUT /v3/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT) to create a pin. Copying a pin can be useful functionality for API developers, but does not represent typical user behavior on Pinterest.

In every new shell, you'll need to activate the virtualenv and configure the environment.

```
$ cd python # from the top of this repository
$ . ./venv/api/bin/activate
$ . ../common/scripts/api_env
```

## Tests

Unit tests are in `./tests/src/` and integrations tests are in `./tests/scripts/`. To run the tests, run the following commands in your virtualenv:
```
$ . ./venv/api/bin/activate # always run in a vitualenv
$ . ../common/scripts/api_env # required for integration tests
$ pip install -r dev-requirements.txt # only needed with a new virtualenv or when requirements change
$ make tests
```
The `Makefile` shows how to run the tests with the `nosetests` command. More information is in the [nose documentation](https://nose.readthedocs.io/en/latest/usage.html).

## PyCharm

If you want to use PyCharm as the IDE for this code, there are two ways
to configure the environment.

1. Set up the environment and run PyCharm at the command line. This is the best way to keep your Pinterest API credentials secure. For example, on MacOS:

   ```
   $ . ../common/scripts/api_env
   $ /Applications/PyCharm\ CE.app/Contents/MacOS/pycharm
   ```

2. Enter the environment variables into the PyCharm environment. Note that PyCharm will store your credentials in its workspace configuration,
which is less secure than keeping the credentials in a file that you control.

   * Print the critical variables.

     ```
     $ . ../common/scripts/api_env
     $ env | grep PINTEREST_APP
     PINTEREST_APP_ID=<number>
     PINTEREST_APP_SECRET=<string>
     $ env | grep HTTPS
     HTTPS_KEY_FILE=<path to key file>
     HTTPS_CERT_FILE=<path to cert file>
     ```

   * Start PyCharm.
   * Select Run/Edit Configurations...
   * Select Templates/Python
   * Enter the four list variables above in the Environment variables.

