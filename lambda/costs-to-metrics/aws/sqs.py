import os
import boto3
import pprint


pp = pprint.PrettyPrinter(indent=4).pprint


def sqs_send_message(message: str):
    queue_url = os.getenv('QUEUE_URL')
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl=queue_url,
        MessageBody=str(message),
    )
    pp(response)
