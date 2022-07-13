import logging
import datetime
from dateutil import parser
from aws.cross_account_client import CrossAccountClient

logger = logging.getLogger()
LINKED_ACCOUNTS = [
    "248804316466",  # digideps-development
    "454262938596",  # digideps-preproduction
    "515688267891",  # digideps-production
    "631181914621",  # identity
    "550790013665",  # lpa-production
    "311462405659",  # management
    "705467933182",  # serve-opg-development
    "540070264006",  # serve-opg-preproduction
    "933639921819",  # serve-opg-production
    "357766484745",  # opg-shared
    "792093328875",  # refunds-development
    "574983609246",  # refunds-production
    "679638075911",  # shared-development
    "997462338508",  # shared-production
    "288342028542",  # sirius-spectrum-development
    "649098267436",  # sirius-spectrum-production
    "653761790766",  # sirius-development
    "492687888235",  # sirius-preproduction
    "313879017102",  # sirius-production
    "367815980639",  # use-my-lpa-development
    "888228022356",  # use-my-lpa-preproduction
    "690083044361",  # use-my-lpa-production
    "050256574573",  # moj-lpa-development
    "987830934591",  # moj-lpa-preproduction
    "980242665824",  # moj-lpa-production
    "936779158973",  # moj-refunds-development
    "764856231715",  # moj-refunds-preproduction
    "805626386523",  # moj-refunds-production
    "132068124730",  # opg-sirius-backup
    "995199299616",  # opg-sandbox
    "238302996107"   # opg-backups
]


class Costs():
    data: dict

    @staticmethod
    def safe_string(value: str) -> str:
        """
        Remove / Replace disallowed characters
        """
        return value.replace(" ", "_").replace("(", "").replace(")", "")

    def service_name_correction(self, name: str) -> str:
        """
        Handle name changes over time to allow for mapping of costs
        """
        if name == 'Amazon EC2 Container Service':
            name = "Amazon Elastic Container Service"
        elif name == 'Amazon Elasticsearch Service':
            name = 'Amazon OpenSearch Service'

        return self.safe_string(name)

    def usage(self, start: datetime, end: datetime, granularity: str = 'DAILY') -> list:
        """
        Get costs of the used resources during this time period
        in a list of dicts
        Group by the account id as well as the service, presuming this would run
        for multiple accounts at once
        """

        with CrossAccountClient('ce') as cost_explorer_client:
            results = []
            linked_accounts_filter = {"And": []}
            dimensions = {"Dimensions": {"Key": "LINKED_ACCOUNT",
                                         "Values": LINKED_ACCOUNTS}}
            linked_accounts_filter = dimensions.copy()
            response = cost_explorer_client.get_cost_and_usage(
                Granularity=granularity,
                TimePeriod={
                    'Start': start.strftime('%Y-%m-%d'),
                    'End': end.strftime('%Y-%m-%d')
                },
                Filter=linked_accounts_filter,
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
                    date = parser.parse(item['TimePeriod']['Start']).replace(
                        tzinfo=datetime.timezone.utc)
                    # if we have cost data, loop over it
                    if 'Groups' in item:
                        for row in item['Groups']:
                            value = float(
                                row['Metrics']['UnblendedCost']['Amount'])
                            # generate package for sending in form that it likes
                            results.append({
                                'metric': {
                                    # this is actually the account id
                                    'Project': self.service_name_correction(row['Keys'][1]),
                                    'Category': 'costs',
                                    'Subcategory': granularity.lower(),
                                    # int - str wrapper is to get a millisecond timestamp,
                                    # but push it as a string
                                    'Time': str(int(date.timestamp() * 1000)),
                                    'MeasureName': self.service_name_correction(row['Keys'][0]),
                                    'MeasureValue': f"{value:.3f}",
                                    "MeasureValueType": "DOUBLE"
                                }
                            })
            return results

    def get(self, start: datetime, end: datetime, granularity: str = 'DAILY') -> list:
        """
        Get used costs for the time period passed
        in for the already set arn & service
        """
        usage = self.usage(start, end, granularity)
        self.data = usage
        return usage
