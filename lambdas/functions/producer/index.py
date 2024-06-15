import json
import uuid
import decimal
import os
import boto3


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


kinesis_client = boto3.client('kinesis')

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

    test_sent_data = {
        "test": "test"
    }

    test_records = [
        {
            "Data": json.dumps(test_sent_data),
            "PartitionKey": str(uuid.uuid4())
        }
        for _ in range(150)
    ]

    # response = kinesis_client.put_record(
    #     StreamName=KINESIS_NAME,
    #     Data=json.dumps(test_sent_data),
    #     PartitionKey=str(uuid.uuid4()),
    # )

    response = kinesis_client.put_records(
        Records=test_records,
        StreamName=KINESIS_NAME
    )

    print(response)
    # print(json.dumps(response, indent=4, cls=DecimalEncoder))

    return 0

    # return {
    #     'statusCode': 200,
    # }
