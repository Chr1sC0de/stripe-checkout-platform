#! /bin/bash

export source_folder=$(dirname -- "${BASH_SOURCE}");

cd "$source_folder/..";

echo "INFO: Setting aws and service provider keys";
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
echo "INFO: Finished setting aws and service provider keys";

echo "INFO: The current aws cli version is: $(aws --version)"
echo "INFO: The current npm version is: $(npm --version)"

if ! [ -x "$(command -v cdk)" ]; then
    echo "INFO: No cdk command, installing";
    npm install -g aws-cdk
    echo "INFO: Finished installing cdk";
fi

echo "INFO: The current cdk version is: $(cdk --version)";

cd ./backend/infrastructure
cdk deploy