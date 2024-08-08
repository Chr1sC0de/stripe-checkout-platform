from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from constructs import Construct


class InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        role = iam.Role.from_role_arn(
            self,
            "SSMParameterRole",
            f"arn:aws:iam::{self.account}:role/aws-service-role/ssm.amazonaws.com/AWSServiceRoleForAmazonSSM",
            mutable=False,
        )
        instance = ec2.Instance(
            self,
            "FrontEndServer",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.lookup,
        )
