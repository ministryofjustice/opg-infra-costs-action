import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AssumeRole:

    def __init__(self):
        self.client = boto3.client('sts')

    def start_session(self, role_arn: str):
        assumed_role = self.client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='opg-costs-to-metrics-lambda',
            DurationSeconds=123,
        )
        logger.info(assumed_role)
        return assumed_role

    def close_session(self):
        self.client.close()
