#! /bin/bash

export source_folder=$(dirname -- "${BASH_SOURCE}");

cd "$source_folder/..";

echo "INFO: Setting aws and service provider keys";

export CURRENT_BRANCH="$(git branch --show-current)"

if [[ $DEVELOPMENT_ENVIRONMENT == auto ]]; then

    echo "INFO: Auto seting environment"
    if [[ $CURRENT_BRANCH == 'release' ]]; then
        export DEVELOPMENT_ENVIRONMENT='prod'
    elif [[ $CURRENT_BRANCH == 'master' ]]; then
        export DEVELOPMENT_ENVIRONMENT='dev0'
    else
        export DEVELOPMENT_ENVIRONMENT='dev1'
    fi
    echo "INFO: Finished auto setting environment: $DEVELOPMENT_ENVIRONMENT"

fi;

if [[ $DEVELOPMENT_ENVIRONMENT == dev* ]]; then
    echo "INFO: Running in development environment: $DEVELOPMENT_ENVIRONMENT";
    export AWS_ACCESS_KEY_ID=$DEV_AWS_ACCESS_KEY_ID;
    export AWS_SECRET_ACCESS_KEY=$DEV_AWS_SECRET_ACCESS_KEY;
    export AWS_SESSION_TOKEN=$DEV_AWS_SESSION_TOKEN;
    export FACEBOOK_CLIENT_ID=$DEV_FACEBOOK_CLIENT_ID;
    export FACEBOOK_CLIENT_SECRET=$DEV_FACEBOOK_CLIENT_SECRET;
elif [[ $DEVELOPMENT_ENVIRONMENT == prod ]]; then
    echo 'ERROR: Product Environment Not Implemented';
    exit 1;
else
    echo "ERROR: Invalid Environment $DEVELOPMENT_ENVIRONMENT"
    exit 1;
fi

echo "INFO: Finished setting aws and service provider keys";

echo "INFO: The current aws cli version is: $(aws --version)";
echo "INFO: The current npm version is: $(npm --version)";

if ! [ -x "$(command -v cdk)" ]; then
    echo "INFO: No cdk command, installing";
    npm install -g aws-cdk;
    echo "INFO: Finished installing cdk";
fi

echo "INFO: The current cdk version is: $(cdk --version)";

cd ./backend/infrastructure;

if [[ $MODE == "deploy" ]]; then
    echo "INFO: Deploying infrastructure";
    cdk deploy;
    echo "INFO: Finished deploying infrastructure";
elif [[ $MODE == "synth" ]]; then
    echo "INFO: Synthesizing infrastructure";
    cdk synth;
    echo "INFO: Finished Synthesizing infrastructure";
elif [[ $MODE == "destroy" ]]; then
    echo "INFO: Destroying infrastructure";
    yes | cdk destroy;
    echo "INFO: Finished destroying infrastructure";
else
    echo "ERROR: Invalid deployment mode: $MODE";
    exit 1;
fi
