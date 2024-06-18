from typing import Any


def adapt_kinesis_shard_count(
        kinesis_client: Any,
        controller_output: int,
        stream_name: str,
        current_active_shard_count: int
    ) -> None:

    if controller_output == current_active_shard_count:
        return

    # Stabilish limits to controller output according to AWS Kinesis limits:
    # https://docs.aws.amazon.com/kinesis/latest/APIReference/API_UpdateShardCount.html

    upper_limit = current_active_shard_count * 2
    lower_limit = current_active_shard_count // 2

    controller_output = max(min(controller_output, upper_limit), lower_limit)

    print(f"Resharding Kinesis from {current_active_shard_count} to {controller_output} shards")

    kinesis_client.update_shard_count(
        StreamName=stream_name, TargetShardCount=controller_output,
        ScalingType="UNIFORM_SCALING"
    )
