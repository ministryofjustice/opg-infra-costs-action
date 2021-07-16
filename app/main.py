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

    # grouped based on the label
    grouped = {}

    for account in args.accounts:
        costings = costs(account['arn'], account['region'], account['label'])
        data = costings.auth().get(start, end)
        label = data['label']
        if label in grouped:
            existing = grouped[label]
            fresh = data['costs']
            for ym in fresh:
                existing[ym]['forecast'] += fresh[ym]['forecast']
                existing[ym]['used'] += fresh[ym]['used']
            grouped[label] = existing

        else:
            grouped[label] = data['costs']

    pp.pprint(grouped)


if __name__ == "__main__":
    try:
        main()
    except Exception as inst:
        print(type(inst))
        print(inst)
        sys.exit(-1)
