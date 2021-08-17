# functions relating to command-line arguments
import argparse


def positive_integer(number):
    ivalue = int(number)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{number} must be a positive integer")
    return ivalue


# TODO: use parent parser.
#       see https://docs.python.org/3/library/argparse.html for details.
def common_arguments(parser):
    """
    Set command line arguments that are common to all of the scripts.
    """
    parser.add_argument("-a", "--access-token", help="access token name")
    parser.add_argument(
        "-l", "--log-level", type=int, default=2, help="level of logging verbosity"
    )
    parser.add_argument(
        "-v", "--api-version", type=positive_integer, help="version of the API to use"
    )
