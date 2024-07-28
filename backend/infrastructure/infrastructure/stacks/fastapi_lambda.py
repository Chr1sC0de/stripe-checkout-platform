import os

from typing import Optional
from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as L
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure import utils


def create_table_from_stripe_object(
    stack: Stack, table_name: str, sort_key: Optional[dynamodb.Attribute] = None
):
    table = dynamodb.TableV2(
        stack,
        table_name,
        table_name=table_name,
        partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        sort_key=None,
        contributor_insights=True,
        removal_policy=(
            RemovalPolicy.DESTROY if "dev" in utils.DEVELOPMENT_ENVIRONMENT else None
        ),
    )
    return table


class InfrastructureStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        company_and_environment = f"{utils.COMPANY}-{utils.DEVELOPMENT_ENVIRONMENT}"

        shared_lambda_kwargs = dict(
            runtime=L.Runtime.PYTHON_3_10,
            handler="entrypoint.handler",
            environment={
                "DEVELOPMENT_LOCATION": "aws",
                "DEVELOPMENT_ENVIRONMENT": utils.DEVELOPMENT_ENVIRONMENT,
            },
        )

        # create the api lambda function
        api = L.Function(
            self,
            f"{company_and_environment}_api",
            code=L.Code.from_asset("../api-lib/dist/lambda.zip"),
            **shared_lambda_kwargs,
        )

        # create the sync-stripe lambda function
        sync_stripe = L.Function(
            self,
            f"{company_and_environment}_stripe_sync",
            timeout=Duration.seconds(900),
            code=L.Code.from_asset("../lambdas/sync-stripe/dist/lambda.zip"),
            **shared_lambda_kwargs,
        )

        for table_name in (
            "product",
            "price",
            "customer",
            "checkout-session-completed",
        ):
            if table_name == "checkout-session-completed":
                sort_key = dynamodb.Attribute(
                    name="customer", type=dynamodb.AttributeType.STRING
                )
            else:
                sort_key = None

            # create the product dynamodb table
            table = create_table_from_stripe_object(
                self, f"{company_and_environment}-{table_name}", sort_key=sort_key
            )

            table.grant_read_write_data(api)
            table.grant_read_write_data(sync_stripe)

        # allow the lambda to access the various ssm parameters
        get_parameter_policy_statement = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            effect=iam.Effect.ALLOW,
            resources=[
                f"arn:aws:ssm:{self.region}:{self.account}:parameter/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/*",
            ],
        )

        # Add IAM policy to allow the lambda to make API HTTP requests on all endpoints
        http_policy_statement = iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            effect=iam.Effect.ALLOW,
            resources=["*"],  # Adjust this to restrict the resources if necessary
        )

        # apply policies to lambda functions

        for lambda_object in (api, sync_stripe):
            lambda_object.add_to_role_policy(get_parameter_policy_statement)
            lambda_object.add_to_role_policy(http_policy_statement)

        # create the function url for the lambda function
        function_url = api.add_function_url(
            auth_type=L.FunctionUrlAuthType.NONE,
            # cross origin resource sharing
            cors=L.FunctionUrlCorsOptions(
                # allow local frontend development
                allowed_origins=["https://0.0.0.0:3000", "https://localhost:3000"],
                allowed_methods=[
                    L.HttpMethod.GET,
                    L.HttpMethod.POST,
                    L.HttpMethod.DELETE,
                ],
                allowed_headers=["Authorization", "Content-Type"],
                allow_credentials=True,
            ),
        )

        # create an ssm parameter pointing to the lambda function url
        ssm.StringParameter(
            self,
            "ssm_api_function_url",
            parameter_name=f"/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/api-function-url",
            string_value=function_url.url,
        )

        # create an ssm parameter for the stripe secret key
        ssm.StringParameter(
            self,
            "ssm_stripe_secret_key",
            parameter_name=f"/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/stripe-secret-key",
            string_value=os.environ["STRIPE_SECRET_KEY"],
        )

        # create an ssm parameter for the stripe webhook secret
        ssm.StringParameter(
            self,
            "ssm_stripe_webhook_secret",
            parameter_name=f"/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/stripe-webhook-secret",
            string_value=os.environ["STRIPE_WEBHOOK_SECRET"],
        )

        # output the link to the endpoint
        CfnOutput(self, "api_url", value=function_url.url)

        self.api_url = function_url.url
