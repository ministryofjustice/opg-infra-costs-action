import argparse
from distutils.util import strtobool
from datetime import datetime
from dateutil.relativedelta import relativedelta

class handler:
    """
    Class to handler all the input variables and parsing passed to the main command.
    """
    args: argparse.Namespace
    arg_parser: argparse.ArgumentParser
    arg_parser_description: str = 'Fetch cost data or generate data table.'

    def dates(self, months: int):
        """
        Return start and end dates based on (current time - months)
        """
        end = datetime.utcnow()
        start = end - relativedelta(months= months)
        start = start.replace(day=1, hour=0, minute=0, second=0)
        return start, end

    def parser(self):
        """
        Construct the argument parser object
        """
        self.arg_parser = argparse.ArgumentParser(description=self.arg_parser_description)
        self.arg_parser.add_argument('--directory', help='Directory to store data files in and read from', default='./')
        self.arg_parser.add_argument('--prefix', help='Prefix to put on generated files', default=datetime.utcnow().strftime('%Y%m%d%H%M%S%f') )

        cost_group = self.arg_parser.add_argument_group("Options for generating cost data per account")
        cost_group.add_argument('--arn', help='AWS ARN to assume')
        cost_group.add_argument('--label', help='Label to name this data', default='None')
        cost_group.add_argument('--region', help='AWS region to operate within', default='eu-west-1')
        cost_group.add_argument('--months', default=6, type=int, help='Number of months ago to start report from.')


        formatting_group = self.arg_parser.add_argument_group("Options to convert cost data into single file.")
        formatting_group.add_argument(
            '--generate-report',
            type=lambda x: bool(strtobool(x)),
            help='If set, this will generate the final markdown file for all data files in directory'
            )

        return self

    def parse(self):
        """
        Parse & validate the input arguments.


        """
        args = self.arg_parser.parse_args()

        if args.generate_report == False:
            if args.arn == None:
                raise Exception('input_handler', 'ARN not passed along')
            elif args.arn != None and len(args.arn) < 1:
                raise Exception('input_handler', 'ARN length too short')

            if args.months == None:
                raise Exception('input_handler', 'Month not passed')
            elif args.months < 1:
                raise Exception('input_handler', 'Month counter has to be between 1 and 12 (found < 1)')
            elif args.months != None and args.months > 12:
                raise Exception('input_handler', 'Month counter has to be between 1 and 12 (found > 12)')

        # no errors, so assign to self
        self.args = args
        return self
