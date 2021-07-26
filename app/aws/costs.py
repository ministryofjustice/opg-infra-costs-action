from typing import Union
import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
from .base import base


class costs(base):
    data: dict
    service: str
    environment: str

    def __init__(self, arn: str, region:str, service:str, environment:str) -> None:
        super().__init__(arn, region)
        self.service = service
        self.environment = environment
        return


    def usage(self, client, start:datetime, end:datetime) -> Union[list, None]:
        """
        Get costs of the used resources during this time period
        in a list of dicts
        """
        results = []
        response =  client.get_cost_and_usage(
            Granularity = 'DAILY',
            TimePeriod = {
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }]
        )

        if 'ResultsByTime' in response:
            for item in response['ResultsByTime']:
                # get the date for this block of costs, making sure to force UTC
                date = parser.parse(item['TimePeriod']['Start']).replace(tzinfo=datetime.timezone.utc)
                # if we have cost data, loop over it
                if 'Groups' in item:
                    for row in item['Groups']:
                        # generate package for sending
                        results.append({
                            'Project': self.service,
                            'Category': 'costs',
                            'SubCategory': 'aws',
                            'environment': self.environment,
                            'Time': int(date.timestamp() * 1000),
                            'MeasureName': row['Keys'][0],
                            'MeasureValue': row['Metrics']['UnblendedCost']['Amount']
                        })

            return results

        return None


    def get(self, start: datetime, end: datetime) -> dict:
        """
        Get used costs for the time period passed
        in for the already set arn & service
        """
        client = self.client('ce')
        usage = self.usage(client, start, end)
        self.data = usage
        return usage
