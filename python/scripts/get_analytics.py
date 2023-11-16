#!/usr/bin/env python
import argparse
import json
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from advertisers import Advertisers
from analytics import AdAnalytics, PinAnalytics, UserAnalytics
from api_config import ApiConfig
from arguments import common_arguments
from oauth_scope import Scope
from user import User
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

    if entity["identifier"]:
        entity_id = entity["identifier"]
        print(f"Using the {kind} with identifier: {entity_id}")
    else:
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
    to download reports for a User, Ad Account, Campaign, Ad Group, or Ad.

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
        choices=[
            "user",
            "pin",
            "ad_account_user",
            "ad_account",
            "campaign",
            "ad_group",
            "ad",
        ],
        help="kind of object used to fetch analytics",
    )
    parser.add_argument("--pin-id", help="Get analytics for this pin identifier.")
    parser.add_argument(
        "--ad-account-id", help="Get analytics for this ad account identifier."
    )
    parser.add_argument(
        "--campaign-id", help="Get analytics for this campaign identifier."
    )
    parser.add_argument(
        "--ad-group-id", help="Get analytics for this ad group identifier."
    )
    parser.add_argument("--ad-id", help="Get analytics for this ad identifier.")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # Specifying identifier at one level requires specifying identifier at levels above.
    if args.campaign_id and not args.ad_account_id:
        parser.error(
            "Ad account identifier must be specified when using campaign identifier"
        )
    if args.ad_group_id and not args.campaign_id:
        parser.error(
            "Campaign identifier must be specified when using ad group identifier"
        )
    if args.ad_id and not args.ad_group_id:
        parser.error("Ad group identifier must be specified when using ad identifier")

    api_config = ApiConfig(verbosity=args.log_level)

    # Requesting pin analytics requires a pin_id.
    if args.analytics_object == "pin" and not args.pin_id:
        parser.error("Pin analytics require a pin identifier.")

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
    user = User(api_config, access_token)
    user_data = user.get()
    user.print_summary(user_data)

    if args.analytics_object == "user":
        # Get analytics for the user account associated with the access token.
        analytics = (
            UserAnalytics(user_data.get("id"), api_config, access_token)
            .last_30_days()
            .metrics({"IMPRESSION", "PIN_CLICK_RATE"})
        )
        results = analytics.get()  # not calling with an ad_account_id argument
    elif args.analytics_object == "pin":
        # Get analytics for the pin.
        analytics = (
            PinAnalytics(args.pin_id, api_config, access_token)
            .last_30_days()
            .metrics({"IMPRESSION", "PIN_CLICK"})
        )
        results = analytics.get(args.ad_account_id)  # ad account id may be None
    elif args.analytics_object == "ad_account_user":
        # Get analytics for the user account associated with an ad account.
        analytics = (
            UserAnalytics(user_data.get("id"), api_config, access_token)
            .last_30_days()
            .metrics({"IMPRESSION", "PIN_CLICK_RATE"})
        )
        advertisers = Advertisers(user_data.get("id"), api_config, access_token)
        # When using find_and_get_analytics, analytics.get() will be called with
        # an ad_account_id argument.
        ads_entities = [
            {
                "object": "ad_account",
                "kind": "Ad Account",
                "parent": "User",
                "get": advertisers.get,
                "analytics": analytics.get,
                "identifier": args.ad_account_id,
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
        advertisers = Advertisers(user_data.get("id"), api_config, access_token)
        ads_entities = [
            {
                "object": "ad_account",
                "kind": "Ad Account",
                "parent": "User",
                "get": advertisers.get,
                "analytics": analytics.get_ad_account,
                "identifier": args.ad_account_id,
            },
            {
                "object": "campaign",
                "kind": "Campaign",
                "parent": "Ad Account",
                "get": advertisers.get_campaigns,
                "analytics": analytics.get_campaign,
                "identifier": args.campaign_id,
            },
            {
                "object": "ad_group",
                "kind": "Ad Group",
                "parent": "Campaign",
                "get": advertisers.get_ad_groups,
                "analytics": analytics.get_ad_group,
                "identifier": args.ad_group_id,
            },
            {
                "object": "ad",
                "kind": "Ad",
                "parent": "Ad Group",
                "get": advertisers.get_ads,
                "analytics": analytics.get_ad,
                "identifier": args.ad_id,
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
