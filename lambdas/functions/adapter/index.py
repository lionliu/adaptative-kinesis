import json
import decimal
import os
import boto3

from monitor import get_last_minute_records


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
    # response = cw_client.list_metrics(
    #     Namespace='AWS/Kinesis',
    #     MetricName='IncomingRecords',
    #     Dimensions=[
    #         {
    #             'Name': 'StreamName',
    #             "Value": KINESIS_NAME
    #         },
    #     ],
    #     # NextToken='string',
    #     RecentlyActive='PT3H',
    #     # IncludeLinkedAccounts=True|False,
    #     # OwningAccount='string'
    # )
    
    total_records = get_last_minute_records(KINESIS_NAME, cw_client, 1)

    print(total_records)
    
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
