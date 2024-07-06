import enum
import os
import time
from typing import Literal, overload

import boto3
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_ssm import SSMClient

COMPANY = os.environ.get("COMPANY", "my-test-company-name")

DEVELOPMENT_LOCATION = os.environ.get("DEVELOPMENT_LOCATION", "local")
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev0")


class SSMParameterName(enum.Enum):
    USER_POOL_PROVIDER_URL = (
        f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-provider-url"
    )
    USER_POOL_COGNITO_COMAIN_URL = (
        f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-cognito-domain-url"
    )
    USER_POOL_ID = f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-id"
    USER_POOL_CLIENT_ID = f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-client-id"
    USER_POOL_SIGNING_KEY = (
        f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-signing-key"
    )

    def __str__(self):
        return self.value


# ---------------------------------------------------------------------------- #
#                         type hints for boto3 clients                         #
# ---------------------------------------------------------------------------- #


@overload
def get_client(service_name: Literal["ssm"]) -> SSMClient: ...


@overload
def get_client(service_name: Literal["dynamodb"]) -> DynamoDBClient: ...


@overload
def get_client(
    service_name: Literal["cognito-idp"],
) -> CognitoIdentityProviderClient: ...


def get_client(service_name: Literal["ssm", "cognito-idp", "dynamodb"]):
    return boto3.client(service_name)


# ---------------------------------------------------------------------------- #
#                              get ssm parameters                              #
# ---------------------------------------------------------------------------- #


def get_ssm_parameter_value(parameter_name: SSMParameterName, max_retries=5) -> str:
    client = get_client("ssm")
    retries = 0
    while retries < max_retries:
        retrieved = client.get_parameter(Name=parameter_name)
        if "Parameter" in retrieved:
            return retrieved["Parameter"]["Value"]
        time.sleep(2**retries)
        retries += 1
    client.close()
    return None
