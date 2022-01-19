#!/usr/bin/env python
import pprint
import dateutil.relativedelta
import datetime
from datetime import timezone
from aws.costs import costs
from send.send import send

pp = pprint.PrettyPrinter(indent=4).pprint



def monthly_costs():
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    """
    # the last full month

    now = datetime.datetime.now(tz=timezone.utc)
    end = now.replace(hour=0, minute=0, second=0, day=1)
    start = end - dateutil.relativedelta.relativedelta(months=1)

    print(f"Getting cost data between [{start}] [{end}]")

    aws_costs = costs()
    results = aws_costs.get(start, end, 'MONTHLY')
    pp(results)

    send(results)

def main():
    """
    Main execution function
    """

    monthly_costs()




if __name__ == "__main__":
    main()
