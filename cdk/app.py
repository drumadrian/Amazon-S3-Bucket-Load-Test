#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import CdkStack
from aws_cdk.core import App, Stack, Tags


app = core.App()
S3LoadTest_stack = CdkStack(app, "S3LoadTest")
Tags.of(S3LoadTest_stack).add("auto-delete","no")
Tags.of(S3LoadTest_stack).add("project","loadtest")

app.synth()
