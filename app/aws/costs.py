from typing import Union
import boto3
import datetime
from dateutil.relativedelta import relativedelta

class costs:
    arn: str
    region:str
    label: str
    session: None

    def __init__(self, arn: str, region:str, label: str) -> None:
        """
        Generate self and attach params to self
        """
        self.arn = arn
        self.label = label
        self.region = region
        return

    def auth(self):
        """
        Set session using creds from env, so requires
        aws-vault usage for local dev
        """
        sts = boto3.client(
            'sts',
            region_name=self.region)

        self.session = sts.assume_role(
            RoleArn=self.arn,
            RoleSessionName='cost_data_sts_session',
            DurationSeconds=900)
        return self

    def client(self):
        """
        Return boto3 client for cost explorer
        """
        return boto3.client(
            'ce',
            region_name = self.region,
            aws_access_key_id = self.session['Credentials']['AccessKeyId'],
            aws_secret_access_key = self.session['Credentials']['SecretAccessKey'],
            aws_session_token = self.session['Credentials']['SessionToken']
        )

    def dates(self, months: int):
        """
        Return start and end dates based on (current time - months)
        """
        end = datetime.datetime.utcnow()
        start = end - relativedelta(months= months)
        start = start.replace(day=1, hour=0, minute=0, second=0)
        return start, end


    def usage(self, client, months: int):
        """
        Get costs of the used resources during this time period
        """
        start, end = self.dates(months)
        return client.get_cost_and_usage(
            Granularity = 'MONTHLY',
            TimePeriod = {
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            }]
        )

    def forecast(self, client) -> Union[None, float]:
        """
        Get forecast data for the rest of this current month & return
        its value
        """
        start = datetime.datetime.utcnow()
        end = start + relativedelta(days=31)
        response = client.get_cost_forecast(
            Granularity = 'MONTHLY',
            TimePeriod = {
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Metric='UNBLENDED_COST'
        )
        if 'Total' in response:
            return float(response['Total']['Amount'])

        return None


    def get(self, months: int):
        """
        """

        client = self.client()

        usage = self.usage(client, months)
        forecast = self.forecast(client)

        return usage
