import argparse
import json
import datetime
from dateutil.relativedelta import relativedelta

class handler:
    """
    Class to handler all the input variables and parsing passed to the main command.
    """
    args: argparse.Namespace
    arg_parser: argparse.ArgumentParser
    arg_parser_description: str = 'Generate cost table for specificed aws accounts.'

    def dates(self, months: int):
        """
        Return start and end dates based on (current time - months)
        """
        end = datetime.datetime.utcnow()
        start = end - relativedelta(months= months)
        start = start.replace(day=1, hour=0, minute=0, second=0)
        return start, end

    def parser(self):
        """
        Construct the argument parser object with all arguments
        """
        self.arg_parser = argparse.ArgumentParser(description=self.arg_parser_description)
        self.arg_parser.add_argument(
                    '--aws-access-key-id',
                    help='AWS access key id property for auth',
                    required=True
                    )
        self.arg_parser.add_argument(
                    '--aws-secret-access-key',
                    help='AWS secret for auth',
                    required=True
                    )
        self.arg_parser.add_argument(
                    '--aws-region',
                    help='AWS region',
                    default='eu-west-1',
                    )
        self.arg_parser.add_argument(
                    '--months',
                    default=6,
                    type=int,
                    help='Number of months ago to start report from.',
                    )
        self.arg_parser.add_argument(
                    '--accounts',
                    default='[]',
                    type=json.loads,
                    help='JSON array of objects containing all account data',
                    )
        return self

    def parse(self):
        """
        Parse & validate the input arguments.

        --accounts must have at least one entry and that must have an arn & label
        --months must be between 1 & 12 due to cost explorer limitations
        """
        args = self.arg_parser.parse_args()

        if len(args.accounts) < 1:
            raise Exception('input_handler', 'Account input parameter invalid')
        else:
            filtered = list(filter(lambda acc: 'arn' in acc and 'label' in acc, args.accounts))
            if len(filtered) != len(args.accounts):
                raise Exception('input_handler', 'One of the accounts passed does not contain both arn & label attributes.')

        if args.months < 1:
            raise Exception('input_handler', 'Month counter has to be between 1 and 12 (found < 1)')
        elif args.months > 12:
            raise Exception('input_handler', 'Month counter has to be between 1 and 12 (found > 12)')

        # no errors, so assign to self
        self.args = args
        return self
