import json
import uuid
import decimal
import os
import boto3
import time

from datetime import datetime, timedelta


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# Get the service clients.
cw_client = boto3.client("cloudwatch")
kinesis_client = boto3.client("kinesis")

# set environment variable
KINESIS_ARN = os.environ['KINESIS_ARN']
KINESIS_NAME = os.environ['KINESIS_NAME']


def handler(event, context):
    # put item in table
    # response = table.put_item(
    #     Item={
    #         'id': str(uuid.uuid4())
    #     }
    # )

    current_timestamp = datetime.now()

    # response = cw_client.list_metrics(
    #     Namespace='AWS/Kinesis',
    #     MetricName='IncomingRecords',
    #     Dimensions=[
    #         {
    #             'Name': 'StreamName',
    #             # 'Value': 'adaptative-kinesis-adaptedkinesisE800CEE2-4AC1a6OW7wkP'
    #             "Value": KINESIS_NAME
    #         },
    #     ],
    #     # NextToken='string',
    #     RecentlyActive='PT3H',
    #     # IncludeLinkedAccounts=True|False,
    #     # OwningAccount='string'
    # )
    
    response = cw_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'adaptedKinesisIncomingRecords',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Kinesis',
                        'MetricName': 'IncomingRecords',
                        'Dimensions': [
                            {
                                'Name': 'StreamName',
                                'Value': KINESIS_NAME
                            },
                        ]
                    },
                    'Period': 30,
                    'Stat': 'Sum',
                    # 'Unit': 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
                },
                # 'Expression': 'string',
                # 'Label': 'string',
                'ReturnData': True,
                # 'Period': 1,
            },
        ],
        StartTime=current_timestamp - timedelta(minutes=1),
        EndTime=current_timestamp,
    )

    # print(response)
    # print(json.dumps(response, indent=4, cls=DecimalEncoder))
    
    # get_stream_description = kinesis_client.describe_stream(
    #     StreamName=KINESIS_NAME,
    # )
    
    # print(get_stream_description)
    
    get_shard = kinesis_client.list_shards(StreamName=KINESIS_NAME)
    
    print(get_shard)
    
    # kinesis_client.update_shard_count(StreamName=KINESIS_NAME, TargetShardCount=2, ScalingType="UNIFORM_SCALING")
    
    # time.sleep(3)
    
    # get_shard = kinesis_client.list_shards(StreamName=KINESIS_NAME)
    
    # print(get_shard)
    
    # kinesis_client.update_shard_count(StreamName=KINESIS_NAME, TargetShardCount=1, ScalingType="UNIFORM_SCALING")
    
    # time.sleep(3)
    
    # get_shard = kinesis_client.list_shards(StreamName=KINESIS_NAME)
    
    # print(get_shard)

    return 0

    # return {
    #     'statusCode': 200,
    # }
