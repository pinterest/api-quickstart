#!/usr/bin/env python
import argparse
import sys
from os.path import abspath, dirname, join

sys.path.append(abspath(join(dirname(__file__), "..", "src")))

from access_token import AccessToken
from api_config import ApiConfig
from arguments import common_arguments
from oauth_scope import Scope
from terms import Terms


def main(argv=[]):
    """
    This script shows how to use the Terms endpoint to
    view related and suggested terms for ads targeting.
    """
    parser = argparse.ArgumentParser(description="Get Related or Suggested Terms")
    parser.add_argument("terms", help="comma-separated list of terms")
    parser.add_argument(
        "-r", "--related", action="store_true", help="get related terms"
    )
    parser.add_argument(
        "-s", "--suggested", action="store_true", help="get suggested terms"
    )
    # limit has to be n because -l is already used for log level
    parser.add_argument("-n", "--limit", type=int, help="limit for suggested terms")
    common_arguments(parser)
    args = parser.parse_args(argv)

    # exactly one of --related or --suggested must be specified
    if not args.related and not args.suggested:
        parser.error("Please specify --related or --suggested")

    if args.related and args.suggested:
        parser.error("Please specify only one of --related or --suggested")

    # --limit can only be used with --suggested
    if args.related and args.limit:
        parser.error("Please do not specify --limit with --related")

    # suggested terms can only take one term
    if args.suggested and "," in args.terms:
        parser.error("Please specify only one term with --suggested")

    # get configuration from defaults and/or the environment
    api_config = ApiConfig(verbosity=args.log_level)

    # Note: It's possible to use the same API configuration with
    # multiple access tokens, so these objects are kept separate.
    access_token = AccessToken(api_config, name=args.access_token)
    access_token.fetch(scopes=[Scope.READ_ADS])

    terms = Terms(api_config, access_token)
    if args.related:
        related_terms = terms.get_related(args.terms)
        terms.print_related_terms(related_terms)
    else:
        suggested_terms = terms.get_suggested(args.terms, limit=args.limit)
        terms.print_suggested_terms(suggested_terms)


if __name__ == "__main__":
    main(sys.argv[1:])
