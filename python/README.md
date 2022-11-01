# Python Quickstart

Python code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring your application ID and application secret.

2. From the top of this repo, change your working directory to this directory:
   ```
   $ cd python
   ```

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

*Note*: In every new shell, you'll need to activate the virtualenv and configure the environment.

```
$ cd python # from the top of this repository
$ . ./venv/api/bin/activate
$ . ../common/scripts/api_env
```

## Additional Functionality

After running the Quick Start, you should be able to run any of the use cases in the scripts directory. Scripts that accept arguments use `argparse`, which ensures that the `-h` or `--help` argument shows usage documentation. In addition, the code for each script has a comment that documents its intended purpose.

Here is a list of common arguments that work with all scripts:
  * `-a <name>` or `--access-token <name>`: The name of the access token for the script. This name is helpful with the `-w` or `--write` option to `get_access_token.py`, which will store the access token in a file that can be used by other scripts.
  * `-l <level>` or `--log-level <level>`: The level of logging verbosity for the script. `0` is only critical output. `1` generates a bit more output. `2` is the default, and prints a lot of useful information for developers learning the API. `3` is maximal verbosity.

Below you will find a description of each script along with an example of its help documentation.

### [get_access_token.py](./scripts/get_access_token.py)
 Quick start code that demonstrates the OAuth 2.0 flow and tests the authentication by reading the user profile using the `/v5/user_account` [endpoint](https://developers.pinterest.com/docs/api/v5/#tag/user_account). Running this script with the `-w` parameter (`./scripts/get_access_token.py -w`) stores the access token in `../common/oauth_tokens/access_token.json` for future use. Use `-w` parameter in combination with the `-a` (access token name) parameter to store separate access tokens for different purposes. When requesting an access token without specifying scopes, the script will default to `user_accounts:read` `pins:read` and `boards:read`. To see a complete list of scopes, refer to the Enums in [`./src/v5/oauth_scope.py`](./src/v5/oauth_scope.py). You can also run `./scripts/get_access_token.py -s help` to see the scopes.

<!--gen-->
```
$ ./scripts/get_access_token.py --help

usage: get_access_token.py [-h] [-w] [-ct] [-s SCOPES] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -w, --write           write access token to file
  -ct, --cleartext      print the token in clear text
  -s SCOPES, --scopes SCOPES
                        comma separated list of scopes or 'help'
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

Use `--scopes help` to get a list of all possible scopes:
<!--gen-->
```
$ ./scripts/get_access_token.py --scopes help

Using application ID and secret from PINTEREST_APP_ID and PINTEREST_APP_SECRET.
Valid OAuth 2.0 scopes for Pinterest API version v5:
  ads:read            Read access to advertising data

  boards:read         Read access to boards
  boards:read_secret  Read access to secret boards
  boards:write        Write access to create, update, or delete boards
  boards:write_secret Write access to create, update, or delete secret boards

  pins:read           Read access to Pins
  pins:read_secret    Read access to secret Pins
  pins:write          Write access to create, update, or delete Pins
  pins:write_secret   Write access to create, update, or delete secret Pins

  user_accounts:read  Read access to user accounts

For more information, see:
  https://developers.pinterest.com/docs/getting-started/scopes/
```

### [refresh_example.py](./scripts/refresh_example.py)

Demonstrates how to refresh an access token. This script is just meant to be self-contained example. Use refresh_access_token if you need to refresh and to store an existing access token.
<!--gen-->
```
$ ./scripts/refresh_example.py --help

usage: refresh_example.py [-h] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Refresh Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```
### [refresh_access_token.py](./scripts/refresh_access_token.py)
 Refreshes an access token stored by using `./scripts/get_access_token.py` with the `-w` (write) argument.
<!--gen-->
```
$ ./scripts/refresh_access_token.py --help

usage: refresh_access_token.py [-h] [-ct] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Refresh Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -ct, --cleartext      print the token in clear text
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_pin.py](./scripts/get_pin.py)
 Retrieves the information for a specific board with the `/v5/pins/{pin_id}` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/pins/get).
<!--gen-->
```
$ ./scripts/get_pin.py --help

usage: get_pin.py [-h] -p PIN_ID [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get a Pin

optional arguments:
  -h, --help            show this help message and exit
  -p PIN_ID, --pin-id PIN_ID
                        pin identifier
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_board.py](./scripts/get_board.py)
 Retrieves the information for a specific board with the `/v5/boards/{board_id}` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/get).
<!--gen-->
```
$ ./scripts/get_board.py --help

usage: get_board.py [-h] -b BOARD_ID [--pins] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get a Board

optional arguments:
  -h, --help            show this help message and exit
  -b BOARD_ID, --board-id BOARD_ID
                        board identifier
  --pins                Get the Pins for the Board
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_user_pins.py](./scripts/get_user_pins.py)
Retrieves all of the pins for a user using several endpoints.
<!--gen-->
```
$ ./scripts/get_user_pins.py --help

usage: get_user_pins.py [-h] [-ps PAGE_SIZE] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get A User's Pins

optional arguments:
  -h, --help            show this help message and exit
  -ps PAGE_SIZE, --page-size PAGE_SIZE
                        Pins per page
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_user_boards.py](./scripts/get_user_boards.py)
Retrieves all of the boards for a user with the `/v5/boards` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/list), using the paging mechanism of the API.
<!--gen-->
```
$ ./scripts/get_user_boards.py --help

usage: get_user_boards.py [-h] [-ps PAGE_SIZE] [--include-empty] [--no-include-empty] [--include-archived] [--no-include-archived]
                          [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get A User's Boards

optional arguments:
  -h, --help            show this help message and exit
  -ps PAGE_SIZE, --page-size PAGE_SIZE
                        Boards per page
  --include-empty       Include empty boards?
  --no-include-empty
  --include-archived    Include archived boards?
  --no-include-archived
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [copy_pin.py](./scripts/copy_pin.py)
Demonstration of how to use the `POST /v5/pins` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/pins/create) to create a pin. Copying a pin can be useful functionality for API developers, but does not represent typical user behavior on Pinterest. Note that `copy_pin.py` can create a video pin from an image pin by suppling the `-m/--media` argument, which is either a Pinterest media identifier (a number) or the path name of a file that contains a video.
<!--gen-->
```
$ ./scripts/copy_pin.py --help

usage: copy_pin.py [-h] -p PIN_ID [-m MEDIA] -b BOARD_ID [-s SECTION] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Copy a Pin

optional arguments:
  -h, --help            show this help message and exit
  -p PIN_ID, --pin-id PIN_ID
                        source pin identifier
  -m MEDIA, --media MEDIA
                        media path or id
  -b BOARD_ID, --board-id BOARD_ID
                        destination board identifier
  -s SECTION, --section SECTION
                        destination board section
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [copy_board.py](./scripts/copy_board.py)
 Demonstration of how to use the `POST /v5/boards` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/create) to create a board. Also uses the `POST /boards/{board_id}/sections` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/create) to create board sections. This script accepts source and target access tokens, so that a board can be copied from one account to another. It also provides an `--all` option that copies all of the boards and pins from a source account into a target account. Copying one or multiple boards can be useful functionality for API developers, but does not represent typical user behavior on Pinterest.
<!--gen-->
```
$ ./scripts/copy_board.py --help

usage: copy_board.py [-h] [-b BOARD_ID] [-n NAME] [-s SOURCE_ACCESS_TOKEN] [-t TARGET_ACCESS_TOKEN] [--all] [--dry-run] [-a ACCESS_TOKEN]
                     [-l LOG_LEVEL]

Copy one Board or all Boards

optional arguments:
  -h, --help            show this help message and exit
  -b BOARD_ID, --board-id BOARD_ID
                        source board identifier
  -n NAME, --name NAME  target board name
  -s SOURCE_ACCESS_TOKEN, --source-access-token SOURCE_ACCESS_TOKEN
                        source access token name
  -t TARGET_ACCESS_TOKEN, --target-access-token TARGET_ACCESS_TOKEN
                        target access token name
  --all                 copy all boards from source to target
  --dry-run             print changes but do not execute them
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_ads.py](./scripts/get_ads.py)
 Reads information about advertiser accounts, campaigns, ad groups, and ads. By default, this script runs in interactive mode to get input on how to descend the advertising object hierarchy. Use the `--all-ads` argument to print all of the information associated with an access token.
<!--gen-->
```
$ ./scripts/get_ads.py --help

usage: get_ads.py [-h] [--all-ads] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Advertisers API Example

optional arguments:
  -h, --help            show this help message and exit
  --all-ads             print all ads information
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [get_analytics.py](./scripts/get_analytics.py)
 Demonstrates how to use the API to retrieve analytics metrics with synchronous requests.
<!--gen-->
```
$ ./scripts/get_analytics.py --help

usage: get_analytics.py [-h] [-o {user,pin,ad_account_user,ad_account,campaign,ad_group,ad}] [--pin-id PIN_ID]
                        [--ad-account-id AD_ACCOUNT_ID] [--campaign-id CAMPAIGN_ID] [--ad-group-id AD_GROUP_ID] [--ad-id AD_ID]
                        [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Get Analytics

optional arguments:
  -h, --help            show this help message and exit
  -o {user,pin,ad_account_user,ad_account,campaign,ad_group,ad}, --analytics-object {user,pin,ad_account_user,ad_account,campaign,ad_group,ad}
                        kind of object used to fetch analytics
  --pin-id PIN_ID       Get analytics for this pin identifier.
  --ad-account-id AD_ACCOUNT_ID
                        Get analytics for this ad account identifier.
  --campaign-id CAMPAIGN_ID
                        Get analytics for this campaign identifier.
  --ad-group-id AD_GROUP_ID
                        Get analytics for this ad group identifier.
  --ad-id AD_ID         Get analytics for this ad identifier.
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

### [analytics_api_example.py](./scripts/analytics_api_example.py)
Demonstrates how to use the API to generate an asynchronous delivery metrics report using the [create](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report) and [get](https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report) endpoints.

<!--gen-->
```
$ ./scripts/analytics_api_example.py --help

usage: analytics_api_example.py [-h] [-a ACCESS_TOKEN] [-l LOG_LEVEL]

Analytics API Example

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
```

## Proxy Configuration

The quickstart uses the [Python Requests](https://docs.python-requests.org) library, which supports the `HTTPS_PROXY` environment variable. For example, to forward Pinterest API requests through a local proxy at port 8080, run this command in the shell before running any of the above commands:
```
$ export HTTPS_PROXY="http://localhost:8080"
```

## Tests

Unit tests are in `./tests/src/` and integrations tests are in `./tests/scripts/`. To run the tests, run the following commands in your virtualenv:
```
$ . ./venv/api/bin/activate # always run in a vitualenv
$ pip install -r dev-requirements.txt # only needed with a new virtualenv or when requirements change
$ make tests
```
The `Makefile` shows how to run the tests with the `pytest` command. More information is in the [pytest documentation](https://docs.pytest.org/).

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
     ```

   * Start PyCharm.
   * Select Run/Edit Configurations...
   * Select Templates/Python
   * Enter the four list variables above in the Environment variables.

## Code Conventions

The code conventions are set by the standard configurations of the [black](https://black.readthedocs.io/en/stable/), [isort](https://pycqa.github.io/isort/), and [flake8](https://flake8.pycqa.org/) linters for python. Run these linters with `make lint`.
