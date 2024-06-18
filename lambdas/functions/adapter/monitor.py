from datetime import datetime, timedelta
from typing import Any


def get_last_minute_average_records(
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
                        'MetricName': 'PutRecords.TotalRecords',
                        'Dimensions': [
                            {
                                'Name': 'StreamName',
                                'Value': stream_name
                            },
                        ]
                    },
                    'Period': 1,
                    'Stat': 'Sum',
                },
                'ReturnData': True,
            },
        ],
        StartTime=current_timestamp - timedelta(minutes=minute_lag + 1),
        EndTime=current_timestamp,
    )

    try:
        fetched_values = get_metric_result["MetricDataResults"][0]["Values"]
        print(get_metric_result["MetricDataResults"])

        return int(max(fetched_values) / (minute_lag * 60))
    except Exception as e:
        print(e)
        return 0


def get_current_active_shard_count(
        stream_name: str,
        kinesis_client: Any,
    ) -> int:

    shards_list = kinesis_client.list_shards(StreamName=stream_name).get("Shards", [])

    active_shard_count = 0

    for shard in shards_list:
        if "SequenceNumberRange" in shard:
            if "EndingSequenceNumber" not in shard["SequenceNumberRange"]:
                active_shard_count += 1

    return active_shard_count
