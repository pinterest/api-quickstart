# Node.js Quickstart

JavaScript code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring your application ID and application secret.

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

After running the Quick Start, you should be able to run any of the use cases in the scripts directory. Scripts that accept arguments use `argparse`, which ensures that the `-h` or `--help` argument shows usage documentation. The code for each script has a comment that documents its intended purpose.
  * `get_access_token.js`: Quick start code that demonstrates the OAuth 2.0 flow and tests the authentication by reading the user profile using the `/v5/user_accounts` [endpoint](https://developers.pinterest.com/docs/v5/#tag/user_accounts) or the `/v3/users/{user}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_user_handler_GET). Running this script with the `-w` parameter (`./scripts/get_access_token.js -w`) stores the access token in `../common/oauth_tokens/access_token.json` for future use. Use `-w` parameter in combination with the `-a` (access token name) parameter to store separate access tokens for different purposes.
  * `refresh_example.js`: Demonstrates how to refresh an access token. This script is just meant to be self-contained example. Use refresh_access_token if you need to refresh and to store an existing access token.
  * `refresh_access_token.js`: Refreshes an access token stored by using `./scripts/get_access_token.js` with the `-w` (write) argument.
  * `get_pin.js`: Retrieves the information for a specific board with the `/v5/pins/{pin_id}` [endpoint](https://developers.pinterest.com/docs/v5/#operation/pins/get) or the `/v3/pins/{pin}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pin_GET).
  * `get_board.js`: Retrieves the information for a specific board with the `/v5/boards/{board_id}` [endpoint](https://developers.pinterest.com/docs/v5/#operation/boards/get) or the `/v3/boards/{board}/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_board_GET).
  * `get_user_pins.js`: Retrieves all of the pins for a user with the `/v3/users/{users}/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_pins_handler_GET), using the paging mechanism of the API. There is not an equivalent v5 endpoint, so this script shows how to emulate the behavior in v5.
  * `get_user_boards.js`: Retrieves all of the boards for a user with the `/v5/boards` [endpoint](https://developers.pinterest.com/docs/v5/#operation/boards/list) or the `/v3/users/{user}/boards/feed/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_user_profile_boards_feed_GET), using the paging mechanism of the API.
  * `copy_pin.js`: Demonstration of how to use the `POST /v5/pins` [endpoint](https://developers.pinterest.com/docs/v5/#operation/pins/create) or the `PUT /v3/pins/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT) to create a pin. Copying a pin can be useful functionality for API developers, but does not represent typical user behavior on Pinterest.
  * `copy_board.js`: Demonstration of how to use the `POST /v3/boards` [endpoint](https://developers.pinterest.com/docs/v5/#operation/boards/create) or the `PUT /v3/boards/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_board_PUT) to create a board. Also uses the `POST /boards/{board_id}/sections` [endpoint](https://developers.pinterest.com/docs/v5/#operation/board_sections/create) or the `PUT /v3/board/{self.board_id}/sections/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_create_section_PUT) to create board sections. This script accepts source and target access tokens, so that a board can be copied from one account to another. It also provides an `--all` option that copies all of the boards and pins from a source account into a target account. Copying one or multiple boards can be useful functionality for API developers, but does not represent typical user behavior on Pinterest.
  * `get_ads.js`: Reads information about advertiser accounts, campaigns, ad groups, and ads. By default, this script runs in interactive mode to get input on how to descend the advertising object hierarchy. Use the `--all-ads` argument to print all of the information associated with an access token.
  * `get_analytics.js`: Demonstrates how to use the API to retrieve analytics metrics with synchronous requests.
  * `get_businesses.js`: Reads the `/v3/users/{user}/businesses/` [endpoint](https://developers.pinterest.com/docs/redoc/#operation/v3_get_linked_business_accounts_GET). This script will generate a 400 error if your application does not have access to the `read_advertisers` scope. To see any data, the authorized account needs to have linked business acounts. There is not an equivalent v5 endpoint.

In every new shell, you'll need to configure the environment.

```
$ cd nodejs # from the top of this repository
$ . ../common/scripts/api_env
```

## Common Command-Line Arguments

In general, use the `-h` or `--help` command-line argument with each script to see a complete list of arguments. Here is a list of common arguments that work with all scripts:
  * `-v <version>` or `--api-version <version>`: The version of the Pinterest API to use. The two choices are `3` and `5`.
  * `-a <name>` or `--access-token <name>`: The name of the access token for the script. This name is helpful with the `-w` or `--write` option to `get_access_token.js`, which will store the access token in a file that can be used by other scripts.
  * `-l <level>` or `--log-level <level>`: The level of logging verbosity for the script. `0` is only critical output. `1` generates a bit more output. `2` is the default, and prints a lot of useful information for developers learning the API. `3` is maximal verbosity.

## Tests

Unit tests use the [Jest framework](https://jestjs.io/) and are in the `*.test.js` files that correspond to each source file. In addition, the [Babel JavaScript compiler](https://babeljs.io/) is required for Jest to run with the module structure used in this repo. The node dependencies for Jest should have been installed as part of the quickstart instructure, Unless you specified the `--production` flag with ```npm install```. To install the `jest` binary, you'll need to run `npm install jest --global` once on your development machine. (These instructions were written when the latest version of `jest` was 27.0.3). Then, run the tests with the `jest` command. No arguments are required, but you can specify the relative pathname of a test file as an argument. For example: `jest ./src/v3/user.test.js`

For compatibility with other languages in this repo, the `Makefile` is set up to run Jest with `make tests`.

## Code Conventions

The code conventions are captured in a set of [rules](.eslintrc.cjs) for [eslint](https://eslint.org/). The configuration is the standard set of rules, with the following modifications:
  * Variables are snake_case instead of camelCase in order to facilitate the task of maintaining parity between the python and nodejs code.
  * The Jest checker emits errors when tests are disabled, per the internal Pinterest standard.
  * Semicolons are used to terminate statements. This convention is debatable but the primary author prefers semicolon syntax for C-like languages.
  * Function declarations have no space between the function name and the open parenthesis. This convention is debatable but the primary author prefers C-style function declarations.
