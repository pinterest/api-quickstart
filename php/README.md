# PHP Quickstart

PHP code that demonstrates the basics of how to use the Pinterest API.

## Quick Start

1. Install PHP and check the version. The code for this repo has been tested with PHP version 8.

1. Follow the directions in the README at the top level of this repo for configuring your application ID and application secret.

3. From the top of this repo, change your working directory to this directory: `cd php`

4. Set up the shell environment.

   ```
   $ . ../common/scripts/api_env
   ```

5. Run the php server in this directory on the port configured when following the instructions in the top-level README.

   ```
   $ php -S localhost:8085
   ```
6. [Click here](http://localhost:8085/) or point your browser at http://localhost:8085.

## Troubleshooting

* If you see the error `Warning: session_start(): Cannot start session when headers already sent`, you're likely using a version of PHP lower than 8. This example requires PHP version 8, so you'll need to install the latest version.

* If the redirect to Pinterest returns a 400 error that says "Oops! You must pass a value for client_id," check to verify that the `api_env` script has been run properly.
   ```
   $ env | grep PINTEREST_APP_ID
   PINTEREST_APP_ID=<your application id>
   ```

* If the demo code that fetches user account information fails, check to make sure that the user account has a profile picture and at least one saved Pin.

## Code Conventions

This PHP code needs to pass the [PHP_CodeSniffer](https://github.com/squizlabs/PHP_CodeSniffer) linter using
the default PEAR coding standard. To run the linter, first install the PHP_CodeSniffer. For example, on MacOS
configured with HomeBrew, install with:
   ```
   brew install php-code-sniffer
   ```
Then, run the linter with `make lint` or `phpcs <filename>`. Run the code fixer
with `make lint-fix` or `phpcbf <filename>`.

`make lint` will be run automatically for pull requests.
