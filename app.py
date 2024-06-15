#!/usr/bin/env python3

from aws_cdk import App

from stacks.adaptative_kinesis_stack import AdaptativeKinesisStack


app = App()
AdaptativeKinesisStack(app, "adaptative-kinesis-stack")

app.synth()
