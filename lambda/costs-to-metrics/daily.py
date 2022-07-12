#!/usr/bin/env python
import datetime
from datetime import timezone
import logging
import dateutil.relativedelta
from aws_xray_sdk.core import patch_all, xray_recorder
from aws.costs import Costs
from send.send import send


logger = logging.getLogger()
logger.setLevel(logging.INFO)
xray_recorder.begin_segment('costs_to_opg_metrics')
patch_all()


def handler(event, context):
    subsegment = xray_recorder.begin_subsegment('costs_to_queue')
    subsegment.put_annotation('service', 'opg_metrics')
    daily_costs()
    xray_recorder.end_subsegment()


def daily_costs():
    """
    Calls the AWS cost explorer api to fetch the unblended cost data
    """
    now = datetime.datetime.now(tz=timezone.utc)
    end = now.replace(hour=0, minute=0, second=0)
    start = end - dateutil.relativedelta.relativedelta(days=1)

    logger.info("Getting cost data between %s and %s", start, end)

    aws_costs = Costs()

    results = aws_costs.get(start, end)

    logger.info(results)

    send(results)


def main():
    """
    Main execution function
    """

    daily_costs()


if __name__ == "__main__":
    main()
