import os
import boto3
from datetime import datetime

from adapt import adapt_kinesis_shard_count
from monitor import (
    get_last_minute_average_records,
    get_current_active_shard_count
)
from controllers import HPAController, PIDController

# Get the service clients.
cw_client = boto3.client("cloudwatch")
kinesis_client = boto3.client("kinesis")

# set environment variable
KINESIS_ARN = os.environ['KINESIS_ARN']
KINESIS_NAME = os.environ['KINESIS_NAME']
EXPERIMENT_NAME = os.environ['EXPERIMENT_NAME']

shared_dict = {
    "prev_error": 0,
    "prev_prev_error": 0,
    "sum_prev_errors": 0,
    "controlled_factor": 1,
}


def handler(event, context):
    global shared_dict

    total_average_records = get_last_minute_average_records(KINESIS_NAME, cw_client, 1)

    current_active_shard_count = get_current_active_shard_count(
        KINESIS_NAME, kinesis_client
    )

    # hpa_controller = HPAController(min_val=1, max_val=5)

    # controller_output = hpa_controller.update(
    #     goal=current_active_shard_count * 1000,
    #     plant_output=total_average_records,
    #     current_controlled_factor=current_active_shard_count
    # )

    pid_controller = PIDController(kp=0.0001, ki=0.0008, kd=0, min_val=1, max_val=5, setpoint=-1)

    controller_output = pid_controller.update(
        goal=current_active_shard_count * 1000,
        plant_output=total_average_records,
        shared_dict=shared_dict,
    )

    print(f"current_active_shard_count: {current_active_shard_count}")
    print(f"total_average_records: {total_average_records}")
    print(f"controller_output: {controller_output}")

    # adapt_kinesis_shard_count(
    #     kinesis_client,
    #     controller_output,
    #     KINESIS_NAME,
    #     current_active_shard_count
    # )

    print({
        "EXPERIMENT_NAME": EXPERIMENT_NAME,
        "total_average_records": total_average_records,
        "goal": current_active_shard_count * 1000,
        "current_active_shard_count": current_active_shard_count,
        "controller_output": controller_output,
        "timestamp": datetime.now().isoformat(),
    })

    return 0
