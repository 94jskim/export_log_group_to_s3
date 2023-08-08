import boto3
from botocore.config import Config


# 마지막 export 상태 확인
def statusCheck(client):
    response = client.describe_export_tasks(limit=1)
    status = response.get('exportTasks')[0].get('status').get('code')

    return status


region = "ap-northeast-2"
config = Config(
    retries={
        'max_attempts': 5,
        'mode': 'standard'
    }
)
client = boto3.client("logs", region_name=region, config=config)

statusCheck(client)
