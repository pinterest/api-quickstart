# functions relating to command-line arguments used by scripts
import argparse


def positive_integer(number):
    ivalue = int(number)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{number} must be a positive integer")
    return ivalue


def common_arguments(parser):
    """
    Set command line arguments that are common to all of the scripts.

    This function should be called after adding arguments, so that the common
    arguments are at the end of the argument list printed as part of the help
    message.

    If this function were implemented as a parent parser, then the common
    arguments would always appear at the beginning of the list provided in the
    command-line help.
    """
    parser.add_argument("-a", "--access-token", help="access token name")
    parser.add_argument(
        "-l", "--log-level", type=int, default=2, help="level of logging verbosity"
    )
    parser.add_argument(
        "-v", "--api-version", type=positive_integer, help="version of the API to use"
    )
