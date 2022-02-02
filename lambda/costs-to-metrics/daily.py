#!/usr/bin/env python
import pprint
import dateutil.relativedelta
import datetime
from datetime import timezone
from aws.costs import costs
from send.send import send


pp = pprint.PrettyPrinter(indent=4).pprint


def handler(event, context):
    daily_costs()


def daily_costs():
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    """
    now = datetime.datetime.now(tz=timezone.utc)
    end = now.replace(hour=0, minute=0, second=0)
    start = end - dateutil.relativedelta.relativedelta(days=1)

    print(f"Getting cost data between [{start}] [{end}]")

    aws_costs = costs()
    results = aws_costs.get(start, end)
    pp(results)

    send(results)


def main():
    """
    Main execution function
    """

    daily_costs()


if __name__ == "__main__":
    main()
