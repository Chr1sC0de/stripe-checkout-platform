import enum
import os
import time
from typing import Literal, overload

import boto3
import boto3.dynamodb.types
import stripe
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_ssm import SSMClient

type_deserializer = boto3.dynamodb.types.TypeDeserializer()
type_serializer = boto3.dynamodb.types.TypeSerializer()

COMPANY = os.environ.get("COMPANY", "my-test-company-name")
DEVELOPMENT_LOCATION = os.environ.get("DEVELOPMENT_LOCATION", "local")
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev0")

COMPANY_AND_ENVIRONMENT = f"{COMPANY}-{DEVELOPMENT_ENVIRONMENT}"

# ---------------------------------------------------------------------------- #
#                                     enums                                    #
# ---------------------------------------------------------------------------- #


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


class DynamoDBTables(enum.Enum):
    PRODUCT = f"{COMPANY_AND_ENVIRONMENT}-product"
    PRICE = f"{COMPANY_AND_ENVIRONMENT}-price"
    CUSTOMER = f"{COMPANY_AND_ENVIRONMENT}-customer"
    CHECKOUT_SESSION_COMPLETED = f"{COMPANY_AND_ENVIRONMENT}-checkout-session-completed"


# ---------------------------------------------------------------------------- #
#                                client methods                                #
# ---------------------------------------------------------------------------- #


@overload
def get_client(service_name: Literal["ssm"]) -> SSMClient: ...


@overload
def get_client(service_name: Literal["dynamodb"]) -> DynamoDBClient: ...


def get_client(service_name: Literal["ssm", "dynamodb"]):
    return boto3.client(service_name)


# ---------------------------------------------------------------------------- #
#                               parameter helpers                              #
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
#                                 sync methods                                 #
# ---------------------------------------------------------------------------- #


def sync_product_price_customer_table():
    client = get_client("dynamodb")
    for name in ("product", "price", "customer"):
        table_name = getattr(DynamoDBTables, name.upper()).value
        objects = getattr(stripe, name.capitalize()).list(limit=100)["data"]
        serialized_products = [p["M"] for p in type_serializer.serialize(objects)["L"]]
        for product in serialized_products:
            update_keys = [k for k in product.keys() if k != "id"]
            client.update_item(
                TableName=table_name,
                Key={"id": product["id"]},
                ExpressionAttributeNames={f"#{k}": k for k in update_keys},
                ExpressionAttributeValues={f":{k}": product[k] for k in update_keys},
                UpdateExpression=f"SET {', '.join([f'#{k}=:{k}' for k in update_keys])}",
            )

    client.close()


def sync_completed_checkout_sessions():
    client = get_client("dynamodb")
    checkout_sessions = stripe.checkout.Session.list(limit=100)["data"]
    for checkout_session in checkout_sessions:
        if checkout_session["customer"] is None:
            checkout_session["customer"] = "N/A"
        checkout_session["line_items"] = stripe.checkout.Session.list_line_items(
            checkout_session["id"]
        )["data"]
        serialized_checkout_session = type_serializer.serialize(checkout_session)["M"]
        update_keys = [
            k for k in checkout_session.keys() if k != "id" and k != "customer"
        ]
        client.update_item(
            TableName=DynamoDBTables.CHECKOUT_SESSION_COMPLETED.value,
            Key={
                "id": serialized_checkout_session["id"],
                "customer": serialized_checkout_session["customer"],
            },
            ExpressionAttributeNames={f"#{k}": k for k in update_keys},
            ExpressionAttributeValues={
                f":{k}": serialized_checkout_session[k] for k in update_keys
            },
            UpdateExpression=f"SET {', '.join([f'#{k}=:{k}' for k in update_keys])}",
        )
    client.close()
