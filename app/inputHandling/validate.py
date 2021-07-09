
from argparse import Namespace


def validate(args: Namespace):
    """
    Validate the arguments passsed in to the script is valid
    """

    if args.token == None:
        raise Exception('Argument Error', 'Missing --token argument')

    if args.months < 1:
        raise Exception('Argument Error', 'Month counter has to be between 1 and 12 (found < 1)')
    elif args.months > 12:
        raise Exception('Argument Error', 'Month counter has to be between 1 and 12 (found > 12)')

    if len(args.accounts) < 2:
        raise Exception('Argument Error', 'Account data has not been passed (length < 2)')
