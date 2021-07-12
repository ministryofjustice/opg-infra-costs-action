from typing import Union
import boto3
import datetime


class base:
    arn: str
    region:str
    session: None

    def __init__(self, arn: str, region:str) -> None:
        """
        Generate self and attach params to self
        """
        self.arn = arn
        self.region = region
        return

    def auth(self):
        """
        Set session using creds from env, so requires
        aws-vault usage for local dev
        """
        sts = boto3.client(
            'sts',
            region_name=self.region)

        self.session = sts.assume_role(
            RoleArn=self.arn,
            RoleSessionName='cost_data_sts_session',
            DurationSeconds=900)
        return self

    def client(self, type: str):
        """
        Return boto3 client for $type
        """
        return boto3.client(
            type,
            region_name = self.region,
            aws_access_key_id = self.session['Credentials']['AccessKeyId'],
            aws_secret_access_key = self.session['Credentials']['SecretAccessKey'],
            aws_session_token = self.session['Credentials']['SessionToken']
        )
