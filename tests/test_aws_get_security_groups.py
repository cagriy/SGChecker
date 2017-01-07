import os
from time import sleep
from unittest import TestCase

import boto3

from main.aws import aws_get_security_groups


class TestAws_get_security_groups(TestCase):
    TEST_REGION = 'eu-west-1'

    def setUp(self):
        self.aws_resource = boto3.resource(
            "ec2",
            aws_access_key_id=os.environ.get('AWS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET'),
            region_name=self.TEST_REGION
        )
        self.security_group = self.aws_resource.create_security_group(GroupName="sgcheck-test-group",
                                                                      Description='SGCheck Test Group - Do Not Use')
        sleep(1)

    def tearDown(self):
        self.security_group.delete(self.security_group.group_id)
        print 1  # TODO: Remove this

    def test_aws_get_security_groups_negative_all_traffic(self):
        self.security_group.authorize_ingress(IpProtocol="-1", CidrIp="1.0.0.0/8", FromPort=20, ToPort=80)
        result = aws_get_security_groups(os.environ.get('AWS_KEY'), os.environ.get('AWS_SECRET'),
                                         self.security_group.group_id)
        self.assertEqual(result, "")
        self.security_group.revoke_ingress(GroupName=self.security_group.group_name, IpProtocol="-1",
                                           CidrIp="1.0.0.0/8", FromPort=20, ToPort=80)

    def test_aws_get_security_groups_positive_all_traffic(self):
        self.security_group.authorize_ingress(IpProtocol="-1", CidrIp="0.0.0.0/0", FromPort=20, ToPort=80)
        result = aws_get_security_groups(os.environ.get('AWS_KEY'), os.environ.get('AWS_SECRET'),
                                         self.security_group.group_id)
        self.assertIn('Critical', result)
        self.assertIn('All ports open to the world !', result)
        self.assertIn(self.TEST_REGION, result)
        self.security_group.revoke_ingress(GroupName=self.security_group.group_name, IpProtocol="-1",
                                           CidrIp="0.0.0.0/0", FromPort=20, ToPort=80)
# TODO: Finish unittests
