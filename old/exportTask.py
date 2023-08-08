import time

import boto3
from botocore.config import Config

# CloudWatch Log Group Export Task
# client = boto3.clinet
# log_group_name = Export Log Group Name
# first_day = start date of export task
# last_day = end date of export task
# destination_bucket = export target bucket name
# destination_prefix = export target prefix


def exportTask(client, log_group_name, first_day, last_day, destination_bucket, destination_prefix):
    try:
        result = client.create_export_task(
            logGroupName=log_group_name,
            fromTime=int(time.mktime(first_day.timetuple())*1000),
            to=int(time.mktime(last_day.timetuple())*1000),
            destination=destination_bucket,
            destinationPrefix=destination_prefix
        )
    except client.exceptions.LimitExceededException:
        print('Error: limit exceed exception, continue')
        return ('continue')

    except Exception as e:
        print('Error: Request to AWS CLI failed {}'.format(e))
        return ('exit')


region = "ap-northeast-2"
config = Config(
    retries={
        'max_attempts': 5,
        'mode': 'standard'
    }
)
client = boto3.client("logs", region_name=region, config=config)

log_group_name = 'i-0f3c4f0ec407ed5e6'


exportTask(client)
