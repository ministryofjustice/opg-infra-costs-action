#!/usr/bin/env python
from argparse import Namespace
import os
import pprint
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import locale

from input.handler import handler
from aws.costs import costs

pp = pprint.PrettyPrinter(indent=4)

# set the locales - use USA as charged in $
# locale.setlocale(locale.LC_ALL, 'en_US')
locale.setlocale(locale.LC_ALL, 'en_GB')


def currency(value):
    """
    template helper to return currency value
    """
    return locale.currency(value, symbol=False, grouping=True)



def costdata(io: handler, args: Namespace):
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    for each month between the start & end dates.

    Save this data as json into a file for processing after
    """
    start, end = io.dates(args.months)
    costings = costs(args.arn, args.region, args.label)
    data = costings.auth().get(start, end)

    file = f"{args.directory}{args.prefix}-{args.label}.costs.json"
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def costreport(io: handler, args: Namespace):
    """
    Finds all costs files generates and merge them together to form
    a data object that is then parsed into a markdown file
    """
    dir = os.path.dirname(os.path.realpath(__file__))
    date = datetime.utcnow().strftime('%Y-%m-%d')

    file_loader = FileSystemLoader(f"{dir}/templates")
    env = Environment(loader=file_loader)
    # add filter
    env.filters.update({'currency': currency})

    grouped = {}
    months = []
    # get list of all cost json files
    files = [pos_json for pos_json in os.listdir(args.directory) if pos_json.endswith('.costs.json')]
    for file in files:
        # load json files and grouped the cost data by the label attribute
        with open(os.path.join(args.directory, file) ) as content:
            data = json.load(content)
            label = data['label']
            months += data['costs'].keys()
            if label in grouped:
                existing = grouped[label]
                fresh = data['costs']
                for ym in fresh:
                    existing[ym]['forecast'] += fresh[ym]['forecast']
                    existing[ym]['used'] += fresh[ym]['used']
                grouped[label] = existing
            else:
                grouped[label] = data['costs']
    # just get the unique months
    months = list(set(months))
    months.sort()
    template = env.get_template('./report-template.txt')
    output = template.render(date=date, months=months, grouped=grouped)

    f = open(os.path.join(args.directory, 'cost_report.html.md.erb'), 'w')
    f.write(output)
    f.close()


def main():
    io = handler()
    args = io.parser().parse().args

    # for i, j in os.environ.items():
    #     print(i, j)

    if args.generate_report == True:
        costreport(io, args)
    else:
        costdata(io, args)


if __name__ == "__main__":
    main()
