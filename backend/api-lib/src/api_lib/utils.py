import enum
import os
import time
from typing import Any, Dict, List, Literal, Optional, overload, Callable

import boto3
import boto3.dynamodb.types
import requests
import stripe
from fastapi import HTTPException
from jose import jwk, jwt
from jose.utils import base64url_decode
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_ssm import SSMClient
from starlette.status import HTTP_401_UNAUTHORIZED

type_deserializer = boto3.dynamodb.types.TypeDeserializer()
type_serializer = boto3.dynamodb.types.TypeSerializer()

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
    SSM_COGNITO_DOMAIN_URL = (
        f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/user-pool-cognito-domain-url"
    )
    SSM_API_FUNCTION_URL = f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/api-function-url"
    SSM_STRIPE_SECRET_KEY = f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/stripe-secret-key"
    SSM_STRIPE_WEBHOOK_SECRET = (
        f"/{COMPANY}/{DEVELOPMENT_ENVIRONMENT}/stripe-webhook-secret"
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


# ---------------------------------------------------------------------------- #
#                            set the stripe api key                            #
# ---------------------------------------------------------------------------- #

stripe.api_key = get_ssm_parameter_value(SSMParameterName.SSM_STRIPE_SECRET_KEY.value)

# ---------------------------------------------------------------------------- #
#                               handle jwt token                               #
# ---------------------------------------------------------------------------- #

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]


def get_user_pool_token_signing_key() -> JWKS:
    return requests.get(
        get_ssm_parameter_value(SSMParameterName.USER_POOL_SIGNING_KEY.value)
    ).json()


def get_hmac_key(token: str, jwks: JWKS) -> Optional[JWK]:
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key


def verify_jwt(token: str) -> bool:
    try:
        jwks = get_user_pool_token_signing_key()
        hmac_key = get_hmac_key(token, jwks)

        if not hmac_key:
            raise ValueError("No pubic key found!")

        hmac_key = jwk.construct(get_hmac_key(token, jwks))

        message, encoded_signature = token.rsplit(".", 1)

        return hmac_key.verify(
            message.encode(), base64url_decode(encoded_signature.encode())
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token, {e}",
        )


# ---------------------------------------------------------------------------- #
#                                 boto3 helpers                                #
# ---------------------------------------------------------------------------- #


def parse_user_attributes(user: dict[str, Any]) -> dict[str, Any]:
    user_attributes = user["UserAttributes"]
    output = {}
    for attribute in user_attributes:
        key = attribute["Name"]
        value = attribute["Value"]
        output[key] = value
    return output


# ---------------------------------------------------------------------------- #
#                        process patition only dynamo db                       #
# ---------------------------------------------------------------------------- #


def process_stripe_single_field_event(
    event_data: Dict[str, Any],
    table: str,
    kind: str,
    event_type: str,
) -> Dict[str, Any]:
    client = get_client(service_name="dynamodb")
    deserialized_data = event_data["data"]["object"]
    serialized_data = type_serializer.serialize(deserialized_data)["M"]

    def create():
        return client.put_item(
            TableName=table,
            Item=serialized_data,
        )

    def update():
        described = client.describe_table(TableName=table)

        keys = [key["AttributeName"] for key in described["Table"]["KeySchema"]]

        key_items = {k: serialized_data[k] for k in keys}

        # create the set expression

        update_expression = "set "
        attribute_values = {}
        expression_attribute_names = {}

        counter = 0

        for k, v in serialized_data.items():
            if k not in key_items.keys():
                expression_attribute_name = f"#{k}"
                update_expression += f"{expression_attribute_name} = :a{counter}, "
                expression_attribute_names[expression_attribute_name] = k
                attribute_values[f":a{counter}"] = v
                counter += 1

        update_expression = update_expression.rstrip(", ")

        return client.update_item(
            TableName=table,
            Key=key_items,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
        )

    def delete() -> Dict[str, Any]:
        described = client.describe_table(TableName=table)

        schema = described["Table"]["KeySchema"]

        keys = [v["AttributeName"] for v in schema]

        items = client.query(
            TableName=table,
            KeyConditionExpression=f"{keys[0]} = :a0",
            ExpressionAttributeValues={":a0": serialized_data[keys[0]]},
        )["Items"]

        responses = []

        for item in items:
            responses.append(
                client.delete_item(TableName=table, Key={k: item[k] for k in keys})
            )
        return responses

    response = "Nothing"

    match event_type:
        case "created":
            response = create()
        case "updated":
            response = update()
        case "deleted":
            response = delete()
    client.close()
    return response
