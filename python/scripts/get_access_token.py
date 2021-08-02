#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments


def main(argv=[]):
    """
    This script retrieves an OAuth 2.0 access token. See the "OAuth Authentication"
    section of the top-level README in this repository for more information.

    The arguments for this script are intended to be used as follows:
     -w / --write :
       Save the access token to a file in JSON format so that it can be used with
       other scripts. The name of the file is based on the 'name' attribute of the
       AccessToken object, which defaults to access_token, so the default file name
       is access_token.json. The directory used to store the file is in the
       PINTEREST_OAUTH_TOKEN_DIR environment variable, which is set to
       ../../common/oauth_tokens/ by the api_env script described in the top-level
       README for this repo. The access_token.json file written by this script may be
       renamed so that it is available for future use. For example,

       renaming access_token.json to my_account_token.json could then be retrieved
       by calling:
         AccessToken(api_config, name='my_account_token').fetch()
     -ct / --cleartext :
       It is best practice not to print credentials like access tokens and refresh
       tokens in clear text, so this script prints SHA256 hashes of tokens so that
       developers can check whether token values have changed. However, engineers
       at Pinterest requested the capability to print tokens in clear text, which
       is implemented using this argument.
     -s / --scopes :
       To provide a quick start for new developers, this script requests an access
       token with the default set of scopes for the application provided in the
       environment (with the PINTEREST_APP_ID and PINTEREST_APP_SECRET variables).
       This argument, which requires a comma-separated list of valid OAuth scopes,
       allows experimentation with different sets of scopes. Specifying scopes prevents
       the access token from being read from the environment or file system, and forces
       the use of the browser-based OAuth process.
    """
    parser = argparse.ArgumentParser(description="Get Pinterest OAuth token")
    parser.add_argument(
        "-w", "--write", action="store_true", help="write access token to file"
    )
    parser.add_argument(
        "-ct", "--cleartext", action="store_true", help="print the token in clear text"
    )
    parser.add_argument("-s", "--scopes", help="comma separated list of scopes")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from oauth_scope import Scope
    from user import User

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    scopes = None  # use the default set of scopes
    if args.scopes:
        # use the comma-separated list of scopes passed as a command-line argument
        scopes = list(map(lambda arg: Scope[arg.upper()], args.scopes.split(",")))
        access_token.oauth(scopes=scopes)
    else:
        try:
            access_token.fetch()
        except ValueError as err:
            # ValueError indicates that something was wrong with the arguments
            print(err)
            parser.print_usage()
            exit(1)

    # Note: It is best practice not to print credentials in clear text.
    # Pinterest engineers asked for this capability to make it easier
    # to support partners.
    if args.cleartext:
        print("Please keep clear text tokens secure!")
        print("clear text access token: " + access_token.access_token)
    print("hashed access token: " + access_token.hashed())
    try:
        if args.cleartext:
            print("clear text refresh token: " + access_token.refresh_token)
        print("hashed refresh token: " + access_token.hashed_refresh_token())
    except Exception:
        print("no refresh token")

    # Save the token, if requested. The comment at the top of this script provides more
    # information about this feature.
    if args.write:
        print("writing access token")
        access_token.write()

    # Use the access token to get information about the user. The purpose of this
    # call is to verify that the access token is working.
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)


# If this script is being called from the command line, call the main function
# with the arguments. The other use case is to call main() from an integration test.
if __name__ == "__main__":
    main(sys.argv[1:])
