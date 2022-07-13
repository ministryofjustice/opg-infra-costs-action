import logging
import os
import boto3


logger = logging.getLogger()


class CrossAccountClient():

    def __init__(self, client_name: str):
        logger.info('boto3 version: %s', boto3.__version__)
        self.sts_client = boto3.client('sts')
        self.role_arn = os.getenv(
            'COST_EXPLORER_ROLE', 'arn:aws:iam::311462405659:role/operator')
        self.client_name = client_name

    def start_session(self, role_arn: str):
        session = self.sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='opg-costs-to-metrics-lambda',
            DurationSeconds=900,
        )
        return session

    def __enter__(self):
        logger.info(
            'Creating cross account session for %s boto3 client...', self.client_name)
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
        # The close method is not available for boto3 v1.20.4, the version provided in the lambda runtime
        # self.sts_client.close()
