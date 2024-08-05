from aws_cdk import Stack
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
        repository = ecr.Repository(
            self,
            f"{utils.COMPANY}-{utils.DEVELOPMENT_ENVIRONMENT}",
            empty_on_delete=True,
        )
