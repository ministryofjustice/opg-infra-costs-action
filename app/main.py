#!/usr/bin/env python
import sys
import pprint

from input.handler import handler
from aws.costs import costs

pp = pprint.PrettyPrinter(indent=4)

def main():
    io = handler()
    args = io.parser().parse().args
    start, end = io.dates(args.months)

    for account in args.accounts:
        pp.pprint(account)
        cost = costs(account['arn'], args.aws_region, account['label'])
        data = cost.auth().get(start, end)
        pp.pprint(data)



if __name__ == "__main__":
    try:
        main()
    except Exception as inst:
        print(type(inst))
        print(inst)
        sys.exit(-1)
