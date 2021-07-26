#!/usr/bin/env python
from argparse import Namespace
import pprint
import locale
import dateutil.relativedelta
import datetime


from input.handler import handler
from aws.costs import costs

pp = pprint.PrettyPrinter(indent=4)


def currency(value):
    """
    template helper to return currency value
    """
    return locale.currency(value, symbol=False, grouping=True)



def costdata(io: handler, args: Namespace):
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    for each month between the start & end dates.

    """
    start = args.start_date
    end = args.end_date
    print(f"[{args.arn}] Getting costs between [{start} - {end}]")
    awscosts = costs(args.arn, args.region, args.service, args.environment)
    results = awscosts.auth().get(start, end)
    pp.pprint(len(results))

    pp.pprint(results[:10])



def main():
    io = handler()
    args = io.parser().parse().args

    costdata(io, args)




if __name__ == "__main__":
    main()
