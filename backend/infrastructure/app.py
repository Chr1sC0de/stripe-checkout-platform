#!/usr/bin/env python3

import os
import re

import aws_cdk as cdk
from infrastructure.stacks import cognito, fastapi_lambda, ecr

company = os.environ.get("COMPANY", "my-test-company-name")

stack_prefix = (
    "".join([a.capitalize() for a in re.sub("[-_]+", " ", company).split(" ")])
    + os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev1").capitalize()
)

app = cdk.App()

FastAPILambdaStack = fastapi_lambda.InfrastructureStack(
    app,
    f"{stack_prefix}FastAPILambdaStack",
)

CognitoStack = cognito.InfrastructureStack(
    app,
    f"{stack_prefix}CognitoStack",
    identity_providers=["facebook"],
    api_url=FastAPILambdaStack.api_url,
)

ECRStack = ecr.InfrastructureStack(
    app,
    f"{stack_prefix}ECRStack",
)

app.synth()
