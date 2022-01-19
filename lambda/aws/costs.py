import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import boto3
import pprint


pp = pprint.PrettyPrinter(indent=4).pprint

class costs():
    data: dict

    def safe_string(self, v:str) -> str:
        """
        Remove / Replace disallowed characters
        """
        return v.replace(" ", "_").replace("(", "").replace(")", "")

    def service_name_correction(self, name:str) -> str:
        """
        Handle name changes over time to allow for mapping of costs
        """
        if name == 'Amazon EC2 Container Service':
            name = "Amazon Elastic Container Service"
        elif name == 'Amazon Elasticsearch Service':
            name = 'Amazon OpenSearch Service'

        return self.safe_string(name)


    def usage(self, start:datetime, end:datetime, granularity:str = 'DAILY') -> list:
        """
        Get costs of the used resources during this time period
        in a list of dicts
        Group by the account id as well as the service, presuming this would run
        for multiple accounts at once
        """
        client = boto3.client('ce')
        results = []
        response =  client.get_cost_and_usage(
            Granularity = granularity,
            TimePeriod = {
                'Start': start.strftime('%Y-%m-%d'),
                'End': end.strftime('%Y-%m-%d')
            },
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }, {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            }]
        )

        if 'ResultsByTime' in response:
            for item in response['ResultsByTime']:
                # get the date for this block of costs, making sure to force UTC
                date = parser.parse(item['TimePeriod']['Start']).replace(tzinfo=datetime.timezone.utc)
                # if we have cost data, loop over it
                if 'Groups' in item:
                    for row in item['Groups']:
                        value = float(row['Metrics']['UnblendedCost']['Amount'])
                        # generate package for sending in form that it likes
                        results.append({
                            'metric': {
                                # this is actually the account id
                                'Project': self.service_name_correction(row['Keys'][1]),
                                'Category': 'costs',
                                'SubCategory': granularity.lower(),
                                # int - str wrapper is to get a millisecond timestamp, but push it as a string
                                'Time': str(int(date.timestamp() * 1000)),
                                'MeasureName': self.service_name_correction(row['Keys'][0]),
                                'MeasureValue': "{:.3f}".format(value),
                                "MeasureValueType": "DOUBLE"
                            }
                        })
        return results


    def get(self, start: datetime, end: datetime, granularity:str = 'DAILY') -> list:
        """
        Get used costs for the time period passed
        in for the already set arn & service
        """
        usage = self.usage(start, end, granularity)
        self.data = usage
        return usage
