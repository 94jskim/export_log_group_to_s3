import datetime
import sys
import time

import boto3
from botocore.config import Config
from dateutil import relativedelta


# -----Define exportTask-----
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
        print('Error: Request to AWS CLI failed: {}'.format(e))
        return (False)

    return (result.get("taskId"))

# -----Define timeset-----
# before_month = REQUIRED, set base export month(0 = now month, 1 = prev month, 2 = -2 month ...)
# range_month = REQUIRED, set export range (1 = befare_month-1, 5 = before_month-5 ...)
# log_group_name = REQUIRED, set export log group name, it replace '/' to '-'
# destination prefix = OPTION, set bucket prefix
# timezone = OPTION, insert your timezone


def timeSet(before_month, range_month, log_group_name, destination_prefix, timezone):
    nowTime = datetime.datetime.utcnow()

    this_month = datetime.datetime(
        year=nowTime.year, month=nowTime.month, day=1, hour=0, minute=0, second=0) - relativedelta.relativedelta(months=before_month)
    prev_month = this_month - relativedelta.relativedelta(months=range_month)
    first_day = prev_month - datetime.timedelta(hours=timezone)
    last_day = this_month - \
        datetime.timedelta(seconds=1) - datetime.timedelta(hours=timezone)
    destination_prefix_val = destination_prefix+'/'+str(
        last_day.year)+'/'+str(last_day.month).zfill(2)+'/'+log_group_name.replace('/', '-')

    return {
        'this_month': this_month,
        'prev_month': prev_month,
        'first_day': first_day,
        'last_day': last_day,
        'destination_prefix': destination_prefix_val
    }

# -----Define export status check-----


def statusCheck(client):
    response = client.describe_export_tasks(limit=1)
    status = response.get('exportTasks')[0].get('status').get('code')

    return status


def script_handler():
    region = "ap-northeast-2"
    config = Config(
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    client = boto3.client("logs", region_name=region, config=config)

    before_month = 0
    range_month = 1
    log_group_name = ["i-08ca478079261f82a",
                      "i-0f3c4f0ec407ed5e6", "/aws/transfer/s-e8acd05227d740a58"]
    destination_prefix_set = "test_prefix"
    timezone = 9
    destination_bucket = "log-group-export-test-bucket"

    time_result = timeSet(before_month, range_month, log_group_name[0],
                          destination_prefix_set, timezone)
#    print(time_result.get("destination_prefix"))

    tries = 120
    for i in range(0, tries):
        task_result = exportTask(client, log_group_name[0], time_result.get("first_day"),
                                 time_result.get("last_day"), destination_bucket, time_result.get("destination_prefix"))
        if task_result == 'continue':
            time.sleep(30)
            continue
        elif task_result == False:
            sys.exit(1)
        else:
            print(task_result)
            break

    return {
        'exportTaskID': task_result,
        'destinationBucket': destination_bucket,
        'destinationPrefix': time_result.get("destination_prefix")
    }


script_handler()
# 받을 변수 Check
# -----Wait for Status-----
# 시작 Wait(아직 Export 중인 작업이 있을 경우 끝날 떄 까지 대기)

# -----aws api execution script -----
# Export List 의 0번 소스를 이용해 작업 시작

# -----Wati for Status-----
# 종료 Wait(시작된 Export Task의 종료를 확인)

# -----api choose-----
# IF Automation Execution Limit Time에 도달했 을 경우?
# 현재 옵션 값 및 제외된 Export List를 가지고 재귀 Automation 실행
# ELIF Export List가 비었을 경우?
# 작업 종료 처리
# Else
# 정의되지 않은 오류
