import json
import os
import time
from unittest import TestCase

import boto3

from main.aws import aws_send_sns_message

SNS_ARN = os.environ.get('SNS_ARN')
AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')


class TestAws_send_sns_message(TestCase):
    def test_aws_send_sns_message(self):
        return #  TODO: Remove
        response = aws_send_sns_message('5', SNS_ARN, AWS_KEY, AWS_SECRET)
        print response['MessageId']
        sqs_arn = SNS_ARN.replace('sns','sqs')
        sqs = boto3.client('sqs',
              aws_access_key_id = AWS_KEY,
              aws_secret_access_key = AWS_SECRET,
              region_name = 'eu-west-1'
        )
        time.sleep(1)
        messages = sqs.receive_message(
            QueueUrl=os.environ.get('SQS_URL'),
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )
        for message in messages['Messages']:
            body = json.loads(message.get('Body'))
            print body['MessageId']
            sqs.delete_message(
                QueueUrl=os.environ.get('SQS_URL'),
                ReceiptHandle=message['ReceiptHandle']
            )



