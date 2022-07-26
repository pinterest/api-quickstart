# Node.js Quickstart

JavaScript code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring your application ID and application secret.

2. From the top of this repo, change your working directory to this directory: 
    ```
    $ cd nodejs
    ```

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

*Note*: In every new shell, you'll need to configure the environment.

```
$ cd nodejs # from the top of this repository
$ . ../common/scripts/api_env
```

## Additional Functionality

After running the Quick Start, you should be able to run any of the use cases in the `scripts/` directory. Scripts that accept arguments use `argparse`, which ensures that the `-h` or `--help` argument shows usage documentation. In addition, the code for each script has a comment that documents its intended purpose.

Here is a list of common arguments that work with all scripts:
  * `-v <version>` or `--api-version <version>`: The version of the Pinterest API to use. The two choices are `3` and `5`.
  * `-a <name>` or `--access-token <name>`: The name of the access token for the script. This name is helpful with the `-w` or `--write` option to `get_access_token.js`, which will store the access token in a file that can be used by other scripts.
  * `-l <level>` or `--log-level <level>`: The level of logging verbosity for the script. `0` is only critical output. `1` generates a bit more output. `2` is the default, and prints a lot of useful information for developers learning the API. `3` is maximal verbosity.


Below you will find a description of each script along with an example of its help documentation.


### [get_access_token.js](./scripts/get_access_token.js)
Quick start code that demonstrates the OAuth 2.0 flow and tests the authentication by reading the user profile using the `/v5/user_account` [endpoint](https://developers.pinterest.com/docs/api/v5/#tag/user_account) or the `/v3/users/{user}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_user_handler_GET). Running this script with the `-w` parameter (`./scripts/get_access_token.js -w`) stores the access token in `../common/oauth_tokens/access_token.json` for future use. Use `-w` parameter in combination with the `-a` (access token name) parameter to store separate access tokens for different purposes. When requesting an access token for v5 without specifying scopes, the script will default to `user_accounts:read` `pins:read` and `boards:read`. The default for v3 is all scopes that are approved for your application. To see a complete list of scopes, refer to the Enums in [`./src/v5/oauth_scope.js`](./src/v5/oauth_scope.js) or [`./src/v3/oauth_scope.js`](./src/v3/oauth_scope.js). You can also run `./scripts/get_access_token.js -s help` to see the scopes for v5 or `./scripts/get_access_token.js -s help -v3` to see the scopes for v3.

<!--gen-->
```
$ ./scripts/get_access_token.js --help

usage: get_access_token.js [-h] [-w] [-ct] [-s SCOPES] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -w, --write           write access token to file
  -ct, --cleartext      print the token in clear text
  -s SCOPES, --scopes SCOPES
                        comma separated list of scopes or "help"
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

Use `--scopes help` to get a list of all possible scopes for v5:
<!--gen-->
```
$ ./scripts/get_access_token.js -v 5 --scopes help

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

Use `--scopes help` to get a list of all possible scopes for v3:
<!--gen-->
```
$ ./scripts/get_access_token.js -v 3 --scopes help

Using application ID and secret from PINTEREST_APP_ID and PINTEREST_APP_SECRET.
Valid OAuth 2.0 scopes for Pinterest API version v3:
  read_domains         Get your website's most clicked Pins, see top saved Pins, etc.
  read_boards          See all your boards (including secret and group boards)
  write_boards         Create new boards and change board settings
  read_pins            See all public Pins and comments
  write_pins           Create new Pins
  read_users           See public data about a user (including boards, following, profile)
  write_users          Change a user's following information
  read_secret_boards   See secret boards
  read_secret_pins     See secret pins
  read_user_followers  Access a user's follows and followers
  write_user_followees Follow things for a user

  read_advertisers     See a user's advertising profile and settings
  write_advertisers    Create and manage a user's advertising profile
  read_campaigns       See data on ad campaigns, including spend, budget and performance
  write_campaigns      Create and manage ad campaigns
  read_merchants       See a user's Catalog (shopping feed)
  write_merchants      Manage a user's Catalog (shopping feed)
  read_pin_promotions  See ads and ad creatives
  write_pin_promotions Create and manage ads and ad creatives

  Composite scopes...
  read_organic         See all of a user's public data.
  write_organic        Create new Pins and boards, update public data
  manage_organic       See, update, and add to public data
  read_secret          See secret boards and secret Pins
  read_ads             See data on ad campaigns, including spend, budget and performance
  write_ads            Manage ad campaigns and see data including spend, budget and performance
  manage_merchants     See and manage a user's Catalog (shopping feed)

For more information, see:
 https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes
```
</details>

### [refresh_example.js](./scripts/refresh_example.js)
Demonstrates how to refresh an access token. This script is just meant to be self-contained example. Use refresh_access_token if you need to refresh and to store an existing access token.

<!--gen-->
```
$ ./scripts/refresh_example.js --help

usage: refresh_example.js [-h] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [refresh_access_token.js](./scripts/refresh_access_token.js)
Refreshes an access token stored by using `./scripts/get_access_token.js` with the `-w` (write) argument.

<!--gen-->
```
$ ./scripts/refresh_access_token.js --help

usage: refresh_access_token.js [-h] [-ct] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Refresh Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -ct, --cleartext      print the token in clear text
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_pin.js](./scripts/get_pin.js)
Retrieves the information for a specific board with the `/v5/pins/{pin_id}` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/pins/get) or the `/v3/pins/{pin}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pin_GET).

<!--gen-->
```
$ ./scripts/get_pin.js --help

usage: get_pin.js [-h] -p PIN_ID [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get A Pin

optional arguments:
  -h, --help            show this help message and exit
  -p PIN_ID, --pin-id PIN_ID
                        pin identifier
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_board.js](./scripts/get_board.js)
Retrieves the information for a specific board with the `/v5/boards/{board_id}` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/get) or the `/v3/boards/{board}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_board_GET).

<!--gen-->
```
$ ./scripts/get_board.js --help

usage: get_board.js [-h] -b BOARD_ID [--pins] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get A Board

optional arguments:
  -h, --help            show this help message and exit
  -b BOARD_ID, --board-id BOARD_ID
                        board identifier
  --pins                Get the Pins for the Board
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_user_pins.js](./scripts/get_user_pins.js)
Retrieves all of the pins for a user with the `/v3/users/{users}/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pins_handler_GET), using the paging mechanism of the API. There is not an equivalent v5 endpoint, so this script shows how to emulate the behavior in v5.

<!--gen-->
```
$ ./scripts/get_user_pins.js --help

usage: get_user_pins.js [-h] [-ps PAGE_SIZE] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get A User's Pins

optional arguments:
  -h, --help            show this help message and exit
  -ps PAGE_SIZE, --page-size PAGE_SIZE
                        Boards per page
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_user_boards.js](./scripts/get_user_boards.js)
Retrieves all of the boards for a user with the `/v5/boards` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/list) or the `/v3/users/{user}/boards/feed/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET), using the paging mechanism of the API.

<!--gen-->
```
$ ./scripts/get_user_boards.js --help

usage: get_user_boards.js [-h] [-ps PAGE_SIZE] [--include-empty] [--no-include-empty] [--include-archived] [--no-include-archived]
                          [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

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
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [copy_pin.js](./scripts/copy_pin.js)
Demonstration of how to use the `POST /v5/pins` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/pins/create) or the `PUT /v3/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT) to create a pin. Copying a pin can be useful functionality for API developers, but does not represent typical user behavior on Pinterest. Note that `copy_pin.js` can create a video pin from an image pin by suppling the `-m/--media` argument, which is either a Pinterest media identifier (a number) or the path name of a file that contains a video.

<!--gen-->
```
$ ./scripts/copy_pin.js --help

usage: copy_pin.js [-h] -p PIN_ID -b BOARD_ID [-m MEDIA] [-s SECTION] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Copy A Pin

optional arguments:
  -h, --help            show this help message and exit
  -p PIN_ID, --pin-id PIN_ID
                        source pin identifier
  -b BOARD_ID, --board-id BOARD_ID
                        destination board identifier
  -m MEDIA, --media MEDIA
                        media path or id
  -s SECTION, --section SECTION
                        destination board section
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [copy_board.js](./scripts/copy_board.js)
Demonstration of how to use the `POST /v3/boards` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/boards/create) or the `PUT /v3/boards/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_board_PUT) to create a board. Also uses the `POST /boards/{board_id}/sections` [endpoint](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/create) or the `PUT /v3/board/{self.board_id}/sections/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_section_PUT) to create board sections. This script accepts source and target access tokens, so that a board can be copied from one account to another. It also provides an `--all` option that copies all of the boards and pins from a source account into a target account. Copying one or multiple boards can be useful functionality for API developers, but does not represent typical user behavior on Pinterest.

<!--gen-->
```
$ ./scripts/copy_board.js --help

usage: copy_board.js [-h] [-b BOARD_ID] [-n NAME] [-s SOURCE_ACCESS_TOKEN] [-t TARGET_ACCESS_TOKEN] [--all] [--dry-run]
                     [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Copy one Board or all Boards

optional arguments:
  -h, --help            show this help message and exit
  -b BOARD_ID, --board-id BOARD_ID
                        destination board identifier
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
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_ads.js](./scripts/get_ads.js)
Reads information about advertiser accounts, campaigns, ad groups, and ads. By default, this script runs in interactive mode to get input on how to descend the advertising object hierarchy. Use the `--all-ads` argument to print all of the information associated with an access token.

<!--gen-->
```
$ ./scripts/get_ads.js --help

usage: get_ads.js [-h] [--all-ads] [--ad-account-id AD_ACCOUNT_ID] [--campaign-id CAMPAIGN_ID] [--ad-group-id AD_GROUP_ID]
                  [--ad-id AD_ID] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Advertisers API Example

optional arguments:
  -h, --help            show this help message and exit
  --all-ads             print all ads information
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
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_analytics.js](./scripts/get_analytics.js)
Demonstrates how to use the API to retrieve analytics metrics with synchronous requests.

<!--gen-->
```
$ ./scripts/get_analytics.js --help

usage: get_analytics.js [-h] [-o {user,pin,ad_account_user,ad_account,campaign,ad_group,ad}] [--pin-id PIN_ID]
                        [--ad-account-id AD_ACCOUNT_ID] [--campaign-id CAMPAIGN_ID] [--ad-group-id AD_GROUP_ID] [--ad-id AD_ID]
                        [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

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
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [get_businesses.js](./scripts/get_businesses.js)
Reads the `/v3/users/{user}/businesses/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_linked_business_accounts_GET). This script will generate a 400 error if your application does not have access to the `read_advertisers` scope. To see any data, the authorized account needs to have linked business acounts. There is not an equivalent v5 endpoint.

<!--gen-->
```
$ ./scripts/get_businesses.js --help

usage: get_businesses.js [-h] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Get Pinterest OAuth token

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

### [analytics_api_example.js](./scripts/analytics_api_example.js)
Demonstrates how to use the API to generate an asynchronous delivery metrics report using the [create](https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/create_async_delivery_metrics_handler) and [get](https://developers.pinterest.com/docs/redoc/adtech_ads_v4/#operation/get_async_delivery_metrics_handler) v4 endpoints, or the [create](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report) and [get](https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report) endpoints for v5.

<!--gen-->
```
$ ./scripts/analytics_api_example.js --help

usage: analytics_api_example.js [-h] [-a ACCESS_TOKEN] [-l LOG_LEVEL] [-v API_VERSION]

Analytics API Example

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        access token name
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        level of logging verbosity
  -v API_VERSION, --api-version API_VERSION
                        version of the API to use
```

## Proxy Configuration

The quickstart uses the [global-agent](https://www.npmjs.com/package/global-agent) package to support proxy configurations. To forward Pinterest API requests through a local proxy at port 8080, run this command in the shell before running any of the above commands:
```
$ export GLOBAL_AGENT_HTTPS_PROXY="http://localhost:8080"
```

According to the [global-agent documentation](https://github.com/gajus/global-agent#what-is-the-reason-global-agentbootstrap-does-not-use-http_proxy), it's also possible to use the more standard HTTPS_PROXY environment variable as follows:
```
$ export GLOBAL_AGENT_ENVIRONMENT_VARIABLE_NAMESPACE=
$ export HTTPS_PROXY="http://localhost:8080"
```

## Tests

Unit tests use the [Jest framework](https://jestjs.io/) and are in the `*.test.js` files that correspond to each source file. In addition, the [Babel JavaScript compiler](https://babeljs.io/) is required for Jest to run with the module structure used in this repo. The node dependencies for Jest should have been installed as part of the quickstart instructure, Unless you specified the `--production` flag with ```npm install```. To install the `jest` binary, you'll need to run `npm install jest --global` once on your development machine. (These instructions were written when the latest version of `jest` was 27.0.3). Then, run the tests with the `jest` command. No arguments are required, but you can specify the relative pathname of a test file as an argument. For example: `jest ./src/v3/user.test.js`

For compatibility with other languages in this repo, the `Makefile` is set up to run Jest with `make tests`.

As of 2022-01-11, the `Browserslist: caniuse-lite is outdated` message appears to be incorrect and can be ignored.

## Code Conventions

The code conventions are captured in a set of [rules](.eslintrc.cjs) for [eslint](https://eslint.org/). The configuration is the standard set of rules, with the following modifications:
  * Variables are snake_case instead of camelCase in order to facilitate the task of maintaining parity between the python and nodejs code.
  * The Jest checker emits errors when tests are disabled, per the internal Pinterest standard.
  * Semicolons are used to terminate statements. This convention is debatable but the primary author prefers semicolon syntax for C-like languages.
  * Function declarations have no space between the function name and the open parenthesis. This convention is debatable but the primary author prefers C-style function declarations.
