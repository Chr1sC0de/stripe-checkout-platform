import aws_cdk as core
import aws_cdk.assertions as assertions

from infrastructure.stacks import cognito


class TestCognito:
    app = core.App()
    stack = cognito.InfrastructureStack(app, "CognitoInfrastructureStack")
    template = assertions.Template.from_stack(stack)

    def test_user_pool_exists(self):
        self.template.resource_count_is("AWS::Cognito::UserPool", 1)

    def test_user_removal_user_policy(self):
        self.template.has_resource(
            "AWS::Cognito::UserPool",
            {"UpdateReplacePolicy": "Delete"},
        )

    def test_domain_exists(self):
        self.template.resource_count_is("AWS::Cognito::UserPoolDomain", 1)

    def test_all_smm_parameters_exist(self):
        self.template.resource_count_is("AWS::SSM::Parameter", 4)
