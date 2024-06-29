#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.stacks import cognito


app = cdk.App()

CognitoStack = cognito.InfrastructureStack(
    app,
    "CognitoStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
    identity_providers=["facebook"],
)

app.synth()
