# Stripe checkout platform

A template for a checkout platform

## Required Secrets and Variables

### Secrets

- DEV_AWS_GITHUB_ACTIONS_ROLE
- DEV_FACEBOOK_CLIENT_ID
- DEV_FACEBOOK_CLIENT_ID

### Variables

- COMPANY
- DEFAULT_AWS_REGION

## Setup OIDC for Github Actions AWS Credentials

OIDC for AWS Github Actions can be configured through the following [Documentation](https://mahendranp.medium.com/configure-github-openid-connect-oidc-provider-in-aws-b7af1bca97dd).
There is an automation [Script](scripts/setup_openid_connect.sh) to help automate the setup of the sysadmin role.

