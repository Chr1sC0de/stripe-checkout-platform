from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_ecr as ecr
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

        ecr.Repository(
            self,
            f"{utils.COMPANY}-{utils.DEVELOPMENT_ENVIRONMENT}",
            empty_on_delete=True if ("dev" in utils.DEVELOPMENT_ENVIRONMENT) else False,
            removal_policy=(
                RemovalPolicy.DESTROY
                if ("dev" in utils.DEVELOPMENT_ENVIRONMENT)
                else RemovalPolicy.RETAIN
            ),
        )
