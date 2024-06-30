#! /bin/bash

# this script sets the aws credentials required to run the cdk to make the deployment

if [[ $DEVELOPMENT_ENVIRONMENT == dev* ]]; then
    echo "INFO: Running in development environment: $DEVELOPMENT_ENVIRONMENT";
    export AWS_ACCESS_KEY_ID=$DEV_AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY=$DEV_AWS_SECRET_ACCESS_KEY
    export AWS_SESSION_TOKEN=$DEV_AWS_SESSION_TOKEN
    export FACEBOOK_CLIENT_ID=$DEV_FACEBOOK_CLIENT_ID
    export FACEBOOK_CLIENT_SECRET=$DEV_FACEBOOK_CLIENT_SECRET
elif [[ $DEVELOPMENT_ENVIRONMENT == prod ]]; then
    echo 'ERRO: Product Environment Not Implemented';
    exit 1;
else
    echo "ERROR: Invalid Environment $DEVELOPMENT_ENVIRONMENT"
    exit 1
fi