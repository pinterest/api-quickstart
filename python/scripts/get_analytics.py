#!/usr/bin/env python
import argparse
import json
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from api_config import ApiConfig
from arguments import common_arguments
from utils import input_number, input_path_for_write


def find_and_get_analytics(
    advertisers, analytics_object, ads_entities, get_args, level
):
    """
    Recursive function that prints out one level of advertising entity
    and then calls itself to print entities at lower levels.
    """
    entity = ads_entities[level]
    kind = entity["kind"]
    entity_list = list(entity["get"](*get_args))
    n_entities = len(entity_list)

    if not n_entities:
        print(f"This {entity['parent']} has no {kind}s.")
        return None

    advertisers.print_enumeration(entity_list, kind)
    # Prompt to get the entity index.
    prompt = f"Please select the {kind} number between 1 and {n_entities}:"
    index = input_number(prompt, 1, n_entities)
    entity_id = entity_list[index - 1]["id"]

    get_args += [entity_id]

    if entity["object"] == analytics_object:
        return entity["analytics"](*get_args)

    level += 1
    if level == len(ads_entities):
        return None

    return find_and_get_analytics(
        advertisers, analytics_object, ads_entities, get_args, level
    )


def main(argv=[]):
    """
    This script shows how to use the Pinterest API synchronous analytics endpoints
    to download reports for a User, Ad Account, Campaign, Ad Group, or Ad. The
    analytics_api_example script shows how to use Pinterest API v3 to retrieve
    similar metrics using asynchronous reporting functionality.

    This script fetches user analytics by default, which just requires an
    access token with READ_USERS scope.

    Using this script for advertising analytics requires a login or an access token
    for a Pinterest user account that has linked Ad Accounts. (The relationship
    between User and Ad Accounts is 1-to-many.) To get a report with useful
    metrics values, at least one linked Ad Account needs to have an active
    advertising campaign. The access token requires READ_USERS and
    READ_ADVERTISERS scopes.
    """
    parser = argparse.ArgumentParser(description="Get Analytics")
    parser.add_argument(
        "-o",
        "--analytics-object",
        default="user",
        choices=["user", "ad_account_user", "ad_account", "campaign", "ad_group", "ad"],
        help="kind of object used to fetch analytics",
    )
    common_arguments(parser)
    args = parser.parse_args(argv)

    api_config = ApiConfig(verbosity=args.log_level, version=args.api_version)

    # This API edge case is best handled up right after API set-up...
    if api_config.version < "v5" and args.analytics_object == "ad_account_user":
        print("User account analytics for shared accounts are")
        print("supported by Pinterest API v5, but not v3 or v4.")
        print("Try using -v5 or an analytics object besides ad_account_user.")
        exit(1)

    # imports that depend on the version of the API
    from access_token import AccessToken
    from advertisers import Advertisers
    from analytics import AdAnalytics, Analytics
    from oauth_scope import Scope
    from user import User

    """
    Fetch an access token and print summary data about the User.
    """

    access_token = AccessToken(api_config, name=args.access_token)
    scopes = [Scope.READ_USERS]
    if args.analytics_object != "user":
        scopes += [Scope.READ_ADVERTISERS]
    access_token.fetch(scopes=scopes)

    # Get the user record. Some versions of the Pinterest API require the
    # user id associated with the access token.
    user_me = User("me", api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    if args.analytics_object == "user":
        # Get analytics for the user account associated with the access token.
        analytics = (
            Analytics(user_me_data.get("id"), api_config, access_token)
            .last_30_days()
            .metrics({"IMPRESSION", "PIN_CLICK_RATE"})
        )
        results = analytics.get()  # not calling with an ad_account_id argument
    elif args.analytics_object == "ad_account_user":
        # Get analytics for the user account associated with an ad account.
        analytics = (
            Analytics(user_me_data.get("id"), api_config, access_token)
            .last_30_days()
            .metrics({"IMPRESSION", "PIN_CLICK_RATE"})
        )
        advertisers = Advertisers(user_me_data.get("id"), api_config, access_token)
        # When using find_and_get_analytics, analytics.get() will be called with
        # an ad_account_id argument.
        ads_entities = [
            {
                "object": "ad_account",
                "kind": "Ad Account",
                "parent": "User",
                "get": advertisers.get,
                "analytics": analytics.get,
            }
        ]
        results = find_and_get_analytics(advertisers, "ad_account", ads_entities, [], 0)
    else:
        # Get advertising analytics for the appropriate kind of object.
        analytics = (
            AdAnalytics(api_config, access_token)
            .last_30_days()
            .metrics({"SPEND_IN_DOLLAR", "TOTAL_CLICKTHROUGH"})
            .granularity("DAY")
        )
        advertisers = Advertisers(user_me_data.get("id"), api_config, access_token)
        ads_entities = [
            {
                "object": "ad_account",
                "kind": "Ad Account",
                "parent": "User",
                "get": advertisers.get,
                "analytics": analytics.get_ad_account,
            },
            {
                "object": "campaign",
                "kind": "Campaign",
                "parent": "Ad Account",
                "get": advertisers.get_campaigns,
                "analytics": analytics.get_campaign,
            },
            {
                "object": "ad_group",
                "kind": "Ad Group",
                "parent": "Campaign",
                "get": advertisers.get_ad_groups,
                "analytics": analytics.get_ad_group,
            },
            {
                "object": "ad",
                "kind": "Ad",
                "parent": "Ad Group",
                "get": advertisers.get_ads,
                "analytics": analytics.get_ad,
            },
        ]
        results = find_and_get_analytics(
            advertisers, args.analytics_object, ads_entities, [], 0
        )

    if not results:
        print("There are no analytics results.")
        return

    # Prompt for the name of an output file and write the analytics results.
    path = input_path_for_write(
        "Please enter a file name for the analytics output:", "analytics_output.json"
    )
    with open(path, "w") as json_file:
        json.dump(results, json_file, indent=2)


if __name__ == "__main__":
    main(sys.argv[1:])
