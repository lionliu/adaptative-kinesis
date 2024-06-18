import aws_cdk as cdk
from aws_cdk import aws_kinesis, aws_lambda, aws_events_targets, aws_events, aws_iam
from aws_cdk import Duration, Stack

from constructs import Construct

CURRENT_EXPERIMENT_NAME = ""

class AdaptativeKinesisStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.adapted_kinesis = aws_kinesis.Stream(
            self,
            id="adapted_kinesis",
            stream_name="adapted_kinesis",
        )

        lambda_base_access = aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")

        self.adapter_lambda_role = aws_iam.Role(
            self,
            id="AdapterLambdaRole",
            role_name="AdapterLambdaRole",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        self.adapter_lambda_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:ListMetrics",
                    "cloudwatch:GetMetricData",
                ],
                resources=["*"],
            )
        )

        self.adapter_lambda_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "kinesis:UpdateShardCount",
                ],
                resources=[self.adapted_kinesis.stream_arn],
            )
        )

        # create adapter lambda function
        self.adapter_lambda = aws_lambda.Function(
            self, "adapter_kinesis_lambda_function",
            function_name="adapter_kinesis_lambda_function",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=aws_lambda.Code.from_asset("./lambdas/functions/adapter"),
            role=self.adapter_lambda_role,
        )

        self.adapter_lambda.role.add_managed_policy(lambda_base_access)


        self.adapted_kinesis.grant_read(self.adapter_lambda)

        self.adapter_lambda.add_environment(
            "KINESIS_ARN", self.adapted_kinesis.stream_arn
        )

        self.adapter_lambda.add_environment(
            "KINESIS_NAME", self.adapted_kinesis.stream_name
        )

        self.adapter_lambda.add_environment(
            "EXPERIMENT_NAME", CURRENT_EXPERIMENT_NAME
        )

        # create a Cloudwatch Event rule
        self.one_minute_rule = aws_events.Rule(
            self, "adapter_kinesis_one_minute_rule",
            schedule=aws_events.Schedule.rate(Duration.minutes(1)),
        )

        self.one_minute_rule.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        self.adapter_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Add target to Cloudwatch Event
        self.one_minute_rule.add_target(
            aws_events_targets.LambdaFunction(self.adapter_lambda)
        )
