import os
import logging
import boto3


logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.INFO)


def sqs_send_message(message: str):
    queue_url = os.getenv('QUEUE_URL')
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl=queue_url,
        MessageBody=str(message),
    )
    logger.info(response)
