from typing import Union
import datetime
from dateutil.relativedelta import relativedelta
from .base import base


class costs(base):
    data: dict
    label: str

    def __init__(self, arn: str, region:str, label:str) -> None:
        super().__init__(arn, region)
        self.label = label
        return


    def usage(self, client, start:datetime, end:datetime) -> Union[dict, None]:
        """
        Get costs of the used resources during this time period
        in a dict with year-month key and value of dict again:

        {
            'arn': 'arn:aws:iam::$account:role/billing',
            'region': 'eu-west-1',
            'label': 'LABEL',
            'costs': {
                '2021-07': {'used': 123.45, 'forecast': 456.0},
                '2021-08': {'used': 765.12}
            }
        }

        """

        response =  client.get_cost_and_usage(
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

        results = {'label': self.label,'arn': self.arn, 'region': self.region, 'costs': {}}

        if 'ResultsByTime' in response:
            for item in response['ResultsByTime']:
                # trim off the day
                month = item['TimePeriod']['Start'][0:-3]
                value = item['Groups'][0]['Metrics']['UnblendedCost']['Amount']
                results['costs'][month] = {'used': float(value), 'forecast': 0.0 }

            return results

        return None


    def forecast(self, client, start) -> Union[None, float]:
        """
        Get forecast data for the rest of this current month & return
        its value
        """
        # always returns the last day of the month
        end = start + relativedelta(days=31)
        response = client.get_cost_forecast(
            Granularity = 'MONTHLY',
            TimePeriod = {
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Metric='UNBLENDED_COST'
        )
        if 'ForecastResultsByTime' in response:
            return float(response['ForecastResultsByTime'][0]['MeanValue'])

        return None


    def get(self, start: datetime, end: datetime) -> dict:
        """
        Get used & forecasted costs for the time period passed
        in for the already set arn & label
        """
        client = self.client('ce')
        usage = self.usage(client, start, end)
        # forecast can only start from today
        forecast = self.forecast(client, end)
        # append forecast for the rest of the month in to this dict
        usage['costs'][end.strftime('%Y-%m')]['forecast'] = forecast
        # set data as this result, also return it
        self.data = usage
        return usage
