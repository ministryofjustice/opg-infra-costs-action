import logging
import os
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AssumeRole:

    def __init__(self):
        self.sts_client = boto3.client('sts')
        self.role_arn = os.getenv('COST_EXPLORER_ROLE')

    def start_session(self, role_arn: str):
        session = self.sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='opg-costs-to-metrics-lambda',
            DurationSeconds=123,
        )
        logger.info(session)
        return session

    def create_client(self, client: str):
        session = self.start_session(self.role_arn)
        boto3_client = boto3.client(
            client,
            region_name='eu-west-1',
            aws_access_key_id=session['Credentials']['AccessKeyId'],
            aws_secret_access_key=session['Credentials']['SecretAccessKey'],
            aws_session_token=session['Credentials']['SessionToken']
        )
        return boto3_client

    def close_session(self):
        self.sts_client.close()
