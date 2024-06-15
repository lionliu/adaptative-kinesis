from datetime import datetime, timedelta
from typing import Any


def get_last_minute_records(
        stream_name: str,
        cloudwatch_client: Any,
        minute_lag: int = 1
    ) -> int:
    current_timestamp = datetime.now()

    get_metric_result = cloudwatch_client.get_metric_data(
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
                                'Value': stream_name
                            },
                        ]
                    },
                    'Period': 30,
                    'Stat': 'Sum',
                },
                # 'Expression': 'string',
                # 'Label': 'string',
                'ReturnData': True,
                # 'Period': 1,
            },
        ],
        StartTime=current_timestamp - timedelta(minutes=minute_lag),
        EndTime=current_timestamp,
    )


    try:
        fetched_values = get_metric_result["MetricDataResults"][0]["Values"]

        return sum(fetched_values)
    except Exception as e:
        print(e)
        return 0
