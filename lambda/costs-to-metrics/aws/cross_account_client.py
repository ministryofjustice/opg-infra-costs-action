import logging
import os
import boto3


logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.INFO)


class CrossAccountClient():

    def __init__(self, client_name: str):
        self.sts_client = boto3.client('sts')
        self.role_arn = os.getenv('COST_EXPLORER_ROLE')
        self.client_name = client_name

    def start_session(self, role_arn: str):
        session = self.sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='opg-costs-to-metrics-lambda',
            DurationSeconds=900,
        )
        logger.info(session)
        return session

    def __enter__(self):
        client_session = self.start_session(self.role_arn)
        boto3_client = boto3.client(
            self.client_name,
            region_name='eu-west-1',
            aws_access_key_id=client_session['Credentials']['AccessKeyId'],
            aws_secret_access_key=client_session['Credentials']['SecretAccessKey'],
            aws_session_token=client_session['Credentials']['SessionToken']
        )
        return boto3_client

    def __exit__(self, type, value, traceback):
        logger.info(
            'Closing underlying endpoint connections for %s boto3 client...', self.client_name)
        self.sts_client.close()
