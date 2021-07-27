#!/usr/bin/env python
from argparse import Namespace
import pprint
import json
import locale
import dateutil.relativedelta
import datetime
import requests

from input.handler import handler
from aws.costs import costs

pp = pprint.PrettyPrinter(indent=4)

def chunks(lst, n):
    """Yield successive n-sized chunks from list (lst)."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def send(args: Namespace, results:list):
    """
    Sends all results from cost explorer to the metrics service
    configured within the args (via key & uri)
    """
    length = len(results)
    chunked = list(chunks(results, 20))
    headers = {'x-api-key': args.key, 'Content-Type': 'application/json; charset=utf-8'}

    print(f"[{args.service}] Sending total of [{length}] metrics in [{len(chunked)}] chunks")
    for i in range(len(chunked)):
        data = chunked[i]
        print(f"[{args.service}] Sending chunk [{i+1}] with [{len(data)}] entries")
        body = {'metrics': data}
        response = requests.put(args.uri, json=body, headers=headers)
        if response.status_code != 200:
            raise Exception('APIResponse', f"Recieved error from API: {response.status_code} = {str(response.json())}")


def costdata(io: handler, args: Namespace):
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    for each month between the start & end dates.

    """
    start = args.start_date
    end = args.end_date

    print(f"[{args.service}-{args.environment}] Getting costs between [{start} - {end}] using [{args.arn}]")
    awscosts = costs(args.arn, args.region, args.service, args.environment)
    results = awscosts.auth().get(start, end)
    #send data to metrics api
    send(args, results)

def main():
    """
    Main execution function
    """
    io = handler()
    args = io.parser().parse().args

    costdata(io, args)




if __name__ == "__main__":
    main()
