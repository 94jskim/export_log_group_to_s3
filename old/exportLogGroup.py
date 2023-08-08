import datetime
import os
import sys
import time

import boto3
import botocore
from botocore.config import Config
from dateutil import relativedelta

paramLogGroupName = ""


region = os.environ['AWS_REGION']

config = Config(
    retries={
        'max_attempts': 5,
        'mode': 'standard'
    }
)
client = boto3.client("logs", region_name=region, config=config)


def script_handler(events, context):
    paramLogGroupName = events.get('logGroupName')
    paramDestination = events.get('destination')
    paramMonthSet = events.get('monthSet')
    paramDestinationPrefix = events.get('destinationPrefix')

    nowTime = datetime.datetime.utcnow()

    thisMonth = datetime.datetime(
        year=nowTime.year, month=nowTime.month + paramMonthSet, day=1, hour=0, minute=0, second=0)
    prevMonth = thisMonth - relativedelta.relativedelta(months=1)
    first_day = prevMonth - datetime.timedelta(hours=2)
    last_day = thisMonth - \
        datetime.timedelta(seconds=1) - datetime.timedelta(hours=2)
    paramDestinationPrefix = paramDestinationPrefix+paramLogGroupName.split('/', maxsplit=1)[0]+'/'+str(
        last_day.year)+'/'+str(last_day.month).zfill(2)+'/'+paramLogGroupName.split('/', maxsplit=1)[1].replace('/', '-')

    tries = 120
    for i in range(tries):
        try:
            result = client.create_export_task(
                logGroupName=paramLogGroupName,
                fromTime=int(time.mktime(first_day.timetuple())*1000),
                to=int(time.mktime(last_day.timetuple())*1000),
                destination=paramDestination,
                destinationPrefix=paramDestinationPrefix
            )
        except client.exceptions.LimitExceededException:
            if i < tries - 1:
                time.sleep(60)
                continue
            else:
                print(
                    'Error: Need to wait until all tasks are finished (LimitExceededException).')
                sys.exit(1)
        except Exception as e:
            print('Error: Request to AWS CLI failed {}'.format(e))
            sys.exit(1)
        break

    print('Export task starting, ID: ' + result.get('taskId'))
    return {
        'exportTaskID': result.get('taskId'),
        'destinationPrefix': paramDestinationPrefix
    }
