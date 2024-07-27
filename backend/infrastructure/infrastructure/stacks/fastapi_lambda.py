import os

from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
)
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as L
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure import utils


def create_table_from_stripe_object(stack: Stack, table_name: str):
    table = dynamodb.TableV2(
        stack,
        table_name,
        table_name=table_name,
        partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
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

        # create the lambda function
        api = L.Function(
            self,
            f"{company_and_environment}_api",
            code=L.Code.from_asset("../api-lib/dist/lambda.zip"),
            runtime=L.Runtime.PYTHON_3_10,
            handler="api.handler",
            environment={
                "DEVELOPMENT_LOCATION": "aws",
                "DEVELOPMENT_ENVIRONMENT": utils.DEVELOPMENT_ENVIRONMENT,
            },
        )

        for table_name in (
            "product",
            "price",
            "customer",
            "checkout-session-completed",
        ):
            # create the product dynamodb table
            table = create_table_from_stripe_object(
                self, f"{company_and_environment}-{table_name}"
            )

            table.grant_read_write_data(api)

        # allow the lambda to access the various ssm parameters
        policy_statement = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            effect=iam.Effect.ALLOW,
            resources=[
                f"arn:aws:ssm:{self.region}:{self.account}:parameter/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/*",
            ],
        )

        api.add_to_role_policy(policy_statement)

        # Add IAM policy to allow the lambda to make API HTTP requests on all endpoints
        http_policy_statement = iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            effect=iam.Effect.ALLOW,
            resources=["*"],  # Adjust this to restrict the resources if necessary
        )

        api.add_to_role_policy(http_policy_statement)

        # create the function url for the lambda function
        function_url = api.add_function_url(
            auth_type=L.FunctionUrlAuthType.NONE,
            # cross origin resource sharing
            cors=L.FunctionUrlCorsOptions(
                allowed_origins=["https://0.0.0.0:3000"],
                allowed_methods=[L.HttpMethod.ALL],
                allowed_headers=["*"],
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
