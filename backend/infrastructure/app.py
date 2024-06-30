#!/usr/bin/env python3

import os
import re

import aws_cdk as cdk
from infrastructure.stacks import cognito

company = os.environ.get("Company", "my-test-company")

stack_prefix = "".join(
    [a.capitalize() for a in re.sub("[-_]+", " ", company).split(" ")]
)

app = cdk.App()

CognitoStack = cognito.InfrastructureStack(
    app,
    f"{stack_prefix}CognitoStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
    identity_providers=["facebook"],
)

app.synth()
