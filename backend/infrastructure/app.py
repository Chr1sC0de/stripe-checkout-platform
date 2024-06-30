#!/usr/bin/env python3

import os
import re

import aws_cdk as cdk
from infrastructure.stacks import cognito

company = os.environ.get("COMPANY", "my-test-company")

stack_prefix = (
    "".join([a.capitalize() for a in re.sub("[-_]+", " ", company).split(" ")])
    + os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev1").capitalize()
)

app = cdk.App()

CognitoStack = cognito.InfrastructureStack(
    app,
    f"{stack_prefix}CognitoStack",
    identity_providers=["facebook"],
)

app.synth()
