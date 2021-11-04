import argparse
from distutils.util import strtobool
import dateutil.relativedelta
import datetime
from datetime import timezone

class handler:
    """
    Class to handler all the input variables and parsing passed to the main command.
    """
    args: argparse.Namespace
    arg_parser: argparse.ArgumentParser
    arg_parser_description: str = 'Push cost data to metrics platform'


    def parser(self):
        """
        Construct the argument parser object
        """
        now = datetime.datetime.now(tz=timezone.utc)
        end = now.replace(hour=0, minute=0, second=0)
        start = end - dateutil.relativedelta.relativedelta(days=1)

        self.arg_parser = argparse.ArgumentParser(description=self.arg_parser_description)

        api_group = self.arg_parser.add_argument_group("API gateway configuration")
        api_group.add_argument('--key',
                            help='API key for access',
                            required=True)
        api_group.add_argument('--uri',
                            help='APIs URI to put data to',
                            required=True)

        aws_group = self.arg_parser.add_argument_group("AWS configuration")
        aws_group.add_argument('--arn',
                            help='AWS ARN to assume',
                            required=True)
        aws_group.add_argument('--region',
                            help='AWS region to operate within',
                            default='eu-west-1')

        ce_group = self.arg_parser.add_argument_group("AWS Cost Explorer options")
        ce_group.add_argument('--start-date',
                            type=datetime.date.fromisoformat,
                            default=start,
                            help=f"Set the start date for this report, defaults to {start}" )
        ce_group.add_argument('--end-date',
                            type=datetime.date.fromisoformat,
                            default=end,
                            help=f"Set the end date for this report, defaults to {end}" )


        service_group = self.arg_parser.add_argument_group("Service details")
        service_group.add_argument('--service',
                            help='Service name to be known as (eg use-an-lpa)',
                            required=True)
        service_group.add_argument('--environment',
                            help='Environment for this service',
                            default='development',
                            choices=['development', 'pre-production', 'production'])


        return self

    def parse(self):
        """
        Parse & validate the input arguments.

        """
        args = self.arg_parser.parse_args()

        args.start_date = args.start_date.date() if type(args.start_date) is datetime.datetime else args.start_date
        args.end_date = args.end_date.date() if type(args.end_date) is datetime.datetime else args.end_date

        # no errors, so assign to self
        self.args = args
        return self
