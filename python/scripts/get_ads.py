#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments
from utils import input_number


def fetch_and_print(advertisers, all_ads, ads_entities, get_args, level):
    """
    Recursive function that prints out one level of advertising entity
    and then calls itself to print entities at lower levels.
    """
    entity = ads_entities[level]
    kind = entity["kind"]
    entity_list = list(entity["get"](*get_args))
    n_entities = len(entity_list)

    if all_ads:
        indent = "  " * level
    else:
        indent = ""

    level += 1

    if not n_entities:
        print(f"{indent}This {entity['parent']} has no {kind}s.")
        return

    if all_ads or level == len(ads_entities):
        entity_range = range(n_entities)
    else:
        advertisers.print_enumeration(entity_list, kind)
        # Prompt to get the entity index.
        prompt = f"Please select the {kind} number between 1 and {n_entities}:"
        index = input_number(prompt, 1, n_entities)
        entity_range = range(index - 1, index)

    for idx in entity_range:
        entity_id = entity_list[idx]["id"]
        if all_ads or level == len(ads_entities):
            summary = f"{indent}{advertisers.summary(entity_list[idx], kind)}"
            print(summary)

        if level < len(ads_entities):
            fetch_and_print(
                advertisers, all_ads, ads_entities, get_args + [entity_id], level
            )


def main(argv=[]):
    """
    This script shows how to use the Pinterest API endpoints to download
    information about Ad Accounts, Campaigns, Ad Groups, and Ads.

    Using this script requires a login or an access token for a Pinterest
    user account that has linked Ad Accounts. (The relationship between User
    and Ad Accounts is 1-to-many.) To get a report with useful metrics values,
    at least one linked Ad Account needs to have an active advertising campaign.
    """
    parser = argparse.ArgumentParser(description="Advertisers API Example")
    parser.add_argument(
        "--all-ads", action="store_true", help="print all ads information"
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from advertisers import Advertisers
    from oauth_scope import Scope
    from user import User

    """
    Step 1: Fetch an access token and print summary data about the User.
    Note that the OAuth will fail if your application does not
    have access to the scope that is required to access
    linked business accounts.
    """

    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_USERS, Scope.READ_ADVERTISERS])

    """
    Sample: Get my user id
    For a future call we need to know the user id associated with
    the access token being used.
    """
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    """
    Step 2: Get Ad Accounts available to my access token and select one of them.
    One of the first challenges many developers run into is that the relationship
    between User and Ad Accounts is 1-to-many.
    In house developers typically don't have login credentials for the main Pinterest
    account of their brand to OAuth against.
    We often reccomend that they set up a new "developer" Pinterest user,
    and then request that this new account is granted access to the
    advertiser account via:
      https://help.pinterest.com/en/business/article/add-people-to-your-ad-account
    This process is also touched on in the API docs:
      https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/Account-Sharing
    """  # noqa: E501 because the long URL is okay
    advertisers = Advertisers(user_me_data.get("id"), api_config, access_token)

    ads_entities = [
        {"kind": "Ad Account", "parent": "User", "get": advertisers.get},
        {"kind": "Campaign", "parent": "Ad Account", "get": advertisers.get_campaigns},
        {"kind": "Ad Group", "parent": "Campaign", "get": advertisers.get_ad_groups},
        {"kind": "Ad", "parent": "Ad Group", "get": advertisers.get_ads},
    ]

    fetch_and_print(advertisers, args.all_ads, ads_entities, [], 0)


if __name__ == "__main__":
    main(sys.argv[1:])
