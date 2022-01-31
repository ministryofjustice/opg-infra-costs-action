import os
import boto3
import pprint


pp = pprint.PrettyPrinter(indent=4).pprint


class send_message():
    def sqs_send_message(log_message):
        queue_url = os.getenv('QUEUE_URL')
        client = boto3.client('sqs')
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=log_message,
        )
        pp(response)
