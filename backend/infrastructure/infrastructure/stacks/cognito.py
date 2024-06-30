import os
from typing import List, Literal

from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ssm as ssm

from constructs import Construct

from infrastructure import utils


class InfrastructureStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        identity_providers: List[Literal["facebook"]] = ["facebook"],
        api_url: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------- Initialize the User pool ------------------------- #

        user_pool = self.create_user_pool()

        # ------------------------- create identity providers ------------------------ #

        for provider in identity_providers:
            self.create_identity_provider(provider, user_pool)

        # ------------ add a cognito domaint to handle the authentication ------------ #

        cognito_domain_prefix = f"{utils.COMPANY}-{utils.ENVIRONMENT}-users"

        user_pool.add_domain(
            "cognito_domain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=cognito_domain_prefix
            ),
        )

        # --------------- add an integration client with oauth enabled --------------- #

        user_pool_client = self.add_integration_clients_to_user_pool(user_pool, api_url)

        ssm.StringParameter(
            self,
            "ssm_user_pool_provider_url",
            parameter_name=f"/{utils.COMPANY}/{utils.ENVIRONMENT}/user-pool-provider-url",
            string_value=user_pool.user_pool_provider_url,
        )

        ssm.StringParameter(
            self,
            "ssm_cognito_domain_url",
            parameter_name=f"/{utils.COMPANY}/{utils.ENVIRONMENT}/user-pool-cognito-domain-url",
            string_value=f"https://{cognito_domain_prefix}.auth.{self.region}.amazoncognito.com",
        )

        ssm.StringParameter(
            self,
            "ssm_user_pool_id",
            parameter_name=f"/{utils.COMPANY}/{utils.ENVIRONMENT}/user-pool-id",
            string_value=user_pool.user_pool_id,
        )

        ssm.StringParameter(
            self,
            "ssm_user_pool_client_id",
            parameter_name=f"/{utils.COMPANY}/{utils.ENVIRONMENT}/user-pool-client-id",
            string_value=user_pool_client.user_pool_client_id,
        )

        ssm.StringParameter(
            self,
            "ssm_user_pool_token_signing_key",
            parameter_name=f"/{utils.COMPANY}/{utils.ENVIRONMENT}/user-pool-signing-key",
            string_value=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool.user_pool_id}/.well-known/jwks.json",
        )

    def add_integration_clients_to_user_pool(
        self, user_pool: cognito.UserPool, api_url: str = None
    ) -> cognito.UserPoolClient:
        callback_urls = []
        if api_url is not None:
            callback_urls.append(f"{api_url}oauth2/token/callback")

        if utils.ENVIRONMENT.startswith("dev"):
            callback_urls.extend(
                [
                    r"https://0.0.0.0:8000/oauth2/token/callback",
                    r"https://www.example.com",
                ]
            )

        return user_pool.add_client(
            "user_pool_integration_client",
            user_pool_client_name=f"{utils.COMPANY}-{utils.ENVIRONMENT}-client-pool",
            auth_flows=cognito.AuthFlow(user_password=True),
            o_auth=cognito.OAuthSettings(callback_urls=callback_urls),
            read_attributes=cognito.ClientAttributes()
            .with_standard_attributes(email_verified=True, email=True)
            .with_custom_attributes("stripe_customer_id"),
        )

    def create_identity_provider(self, name: str, user_pool: cognito.UserPool) -> None:
        name_upper = name.upper()
        name_lower = name.lower()

        client_id_environment_variable = f"{name_upper}_CLIENT_ID"
        client_secret_environment_variable = f"{name_upper}_CLIENT_SECRET"

        client_id = os.environ.get(client_id_environment_variable, None)
        client_secret = os.environ.get(client_secret_environment_variable, None)

        for check, variable in zip(
            [client_id, client_secret],
            [client_id_environment_variable, client_secret_environment_variable],
        ):
            assert (
                check is not None
            ), f"ERROR: {client_id_environment_variable} is None, please set before attempting to deploy"

        cognito.UserPoolIdentityProviderFacebook(
            self,
            f"{name_lower}_identity_provider",
            user_pool=user_pool,
            client_id=client_id,
            client_secret=client_secret,
            attribute_mapping=cognito.AttributeMapping(
                email=getattr(cognito.ProviderAttribute, f"{name_upper}_EMAIL")
            ),
            scopes=["email", "public_profile"],
        )

    def create_user_pool(self: Stack) -> cognito.UserPool:
        return cognito.UserPool(
            self,
            "user_pool",
            user_pool_name=f"{utils.COMPANY}-{utils.ENVIRONMENT}-user-pool",
            account_recovery=cognito.AccountRecovery.PHONE_WITHOUT_MFA_AND_EMAIL,
            advanced_security_mode=None,
            auto_verify=cognito.AutoVerifiedAttrs(email=True, phone=False),
            custom_attributes={
                "stripe_customer_id": cognito.StringAttribute(mutable=True),
            },
            custom_sender_kms_key=None,
            deletion_protection=None,
            device_tracking=None,
            email=None,
            enable_sms_role=None,
            keep_original=None,
            lambda_triggers=None,
            mfa=None,
            mfa_message=None,
            mfa_second_factor=None,
            password_policy=None,
            removal_policy=RemovalPolicy.DESTROY,
            self_sign_up_enabled=None,
            sign_in_aliases=None,
            sign_in_case_sensitive=None,
            sms_role=None,
            sms_role_external_id=None,
            sns_region=None,
            standard_attributes=None,
            user_invitation=None,
            # TODO: This currently causes errors in outlook due to security
            # We need to handle email verification
            user_verification=cognito.UserVerificationConfig(
                email_style=cognito.VerificationEmailStyle.LINK
            ),
        )
