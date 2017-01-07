from __future__ import print_function
import boto3
import json
import os
from time import sleep
from pprint import pprint

RISKY_PORTS = [20, 21, 22, 1433, 1434, 3306, 3389, 4333, 5432, 5500]

template = """
Security Group Alert !
Alert Level : {0}
Account: {1}
Region: {2}
Group Id: {3}
Detail: {4}

"""


def aws_get_regions(aws_key, aws_secret):
    aws_client = boto3.client(
        "ec2",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name='eu-west-1'
    )
    response = aws_client.describe_regions()
    result = []
    for region in response['Regions']:
        result.append(region['RegionName'])
    return result


def aws_get_security_groups(aws_key, aws_secret, test_sg=""):
    # TODO: Requires Unit Testing
    global message
    for region in aws_get_regions(aws_key, aws_secret):
        aws_client = boto3.client(
            "ec2",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=region
        )
        message = ""

        response = aws_client.describe_security_groups()
        account = response['SecurityGroups'][0]['OwnerId']
        for security_group in response['SecurityGroups']:
            # message = ""
            for ip_permissions in security_group['IpPermissions']:
                pprint(security_group)
                affected_ports = []
                if ip_permissions['IpProtocol'] == '-1' and '0.0.0.0/0' in str(ip_permissions['IpRanges']) and \
                        (test_sg == '' or security_group['GroupId'] == test_sg):
                    message += template.format('Critical', account, region, security_group['GroupId'],
                                               'All ports open to the world !')
                if ip_permissions['IpProtocol'] == 'tcp' and '0.0.0.0/0' in str(ip_permissions['IpRanges']) and \
                        (test_sg == '' or security_group['GroupId'] == test_sg):
                    from_port = ip_permissions['FromPort']
                    to_port = ip_permissions['ToPort']
                    for port in RISKY_PORTS:
                        if from_port <= port <= to_port:
                            affected_ports.append(port)
                    if len(affected_ports) > 0:
                        message += template.format('Important', account, region, security_group['GroupId'],
                                                   'TCP port(s) ' + ",".join(
                                                       str(x) for x in affected_ports) + ' open to the world !')
                    else:
                        message += template.format('Warning', account, region, security_group['GroupId'],
                                                   'TCP port' + (
                                                       ' ' + str(to_port) if to_port == from_port else 's from ' + str(
                                                           from_port) + ' to ' + str(to_port)) + ' open to the world !')
                if message != "":
                    print(message)
                    aws_send_sns_message(message, os.environ.get('SNS_ARN'), aws_key, aws_secret)

                if security_group['GroupId'] == test_sg:
                    return message

        sleep(1)  # Not to overload AWS API
    return message


def aws_send_sns_message(message, topic_arn, aws_key, aws_secret):
    # type: (string, string, string, string) -> string
    # TODO: Requires Unit Testing
    topic_keys = topic_arn.split(':', 5)
    region = topic_keys[3]
    aws_client = boto3.client(
        "sns",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=region
    )
    response = aws_client.publish(
        TopicArn=os.environ.get('SNS_ARN'),
        Message=message
    )
    return response





