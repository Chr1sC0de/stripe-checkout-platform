from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure import utils


class InfrastructureStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = ecr.Repository(
            self,
            "General",
            empty_on_delete=True if ("dev" in utils.DEVELOPMENT_ENVIRONMENT) else False,
            removal_policy=(
                RemovalPolicy.DESTROY
                if ("dev" in utils.DEVELOPMENT_ENVIRONMENT)
                else RemovalPolicy.RETAIN
            ),
        )

        ssm.StringParameter(
            self,
            "ssm_ect_general_repository_name",
            parameter_name=f"/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/ecr-general-repository-name",
            string_value=repository.repository_name,
        )

        ssm.StringParameter(
            self,
            "ssm_ect_general_repository_uri",
            parameter_name=f"/{utils.COMPANY}/{utils.DEVELOPMENT_ENVIRONMENT}/ecr-general-repository-uri",
            string_value=repository.repository_uri,
        )
