#!/usr/bin/env python
import argparse
import sys
import time
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments


def main(argv=[]):
    """
    This script extends the example in get_access_token.py by demonstrating
    how to use the OAuth refresh token to obtain a new access token.
    It executes the refresh twice, verifying each time that the access token
    has actually changed and that the new access token can be used to access
    the associated user's profile.
    """
    parser = argparse.ArgumentParser(description="Refresh Pinterest OAuth token")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from user import User

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch()
    hashed = access_token.hashed()
    access_token_hashes = [hashed]

    print("hashed access token: " + hashed)
    print("hashed refresh token: " + access_token.hashed_refresh_token())

    # use the access token to get information about the user
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    # Doing refreshes too quickly can result in the same access_token being generated.
    # In practice, this isn't a problem because tokens should be refreshed after
    # relatively long periods of time.
    print("wait a second to avoid getting the same token on the first refresh...")
    time.sleep(1)

    # refresh the access_token
    # Note that the AccessToken encapsulates the credentials,
    # so there is no need to refresh the User or other objects.
    access_token.refresh()
    hashed = access_token.hashed()
    assert hashed not in access_token_hashes
    access_token_hashes.append(hashed)

    # This call demonstrates that the access_token has changed
    # without printing the actual token.
    print("hashed access token: " + hashed)

    print("accessing with refreshed access_token...")
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    print("wait a second to avoid getting the same token on the second refresh...")
    time.sleep(1)

    # refresh the access_token again
    access_token.refresh()

    # Verify that the access_token has changed again.
    hashed = access_token.hashed()
    assert hashed not in access_token_hashes
    access_token_hashes.append(hashed)
    print("hashed access token: " + hashed)

    print("accessing with second refreshed access_token...")
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)


if __name__ == "__main__":
    main(sys.argv[1:])
