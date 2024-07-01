#! /bin/bash

if [[ -d ~/.aws/config ]]; then
    rm ~/.aws/config
fi

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder/.." || exit

echo "INFO: Setting aws and service provider keys"

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

fi

if [[ $DEVELOPMENT_ENVIRONMENT == dev* ]]; then
    echo "INFO: Running in development environment: $DEVELOPMENT_ENVIRONMENT"
    export AWS_ACCESS_KEY_ID=$DEV_AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY=$DEV_AWS_SECRET_ACCESS_KEY
    export AWS_SESSION_TOKEN=$DEV_AWS_SESSION_TOKEN
    export FACEBOOK_CLIENT_ID=$DEV_FACEBOOK_CLIENT_ID
    export FACEBOOK_CLIENT_SECRET=$DEV_FACEBOOK_CLIENT_SECRET
elif [[ $DEVELOPMENT_ENVIRONMENT == prod ]]; then
    echo 'ERROR: Production Environment Not Implemented'
    exit 1
else
    echo "ERROR: Invalid Environment $DEVELOPMENT_ENVIRONMENT"
    exit 1
fi

echo "INFO: Finished setting aws and service provider keys"

echo "INFO: The current aws cli version is: $(aws --version)"
echo "INFO: The current npm version is: $(npm --version)"

if ! [ -x "$(command -v cdk)" ]; then
    echo "INFO: No cdk command, installing"
    npm install -g aws-cdk
    echo "INFO: Finished installing cdk"
fi

echo "INFO: The current cdk version is: $(cdk --version)"

cd ./backend/infrastructure

# bootstrap the environment if it has not been run before

if [[ $MODE != 'synth' ]]; then

    echo "INFO: Checking if Bootstrap exists"

    export STACK_EXISTS=$(aws cloudformation describe-stacks --stack-name "CDKToolkit" 2>&1)

    # # Check if the bootstrap stack exists
    if [[ $STACK_EXISTS == *"does not exist"* ]]; then
        echo "INFO: Bootstrap stack does not exist. Running CDK bootstrap..."
        cdk bootstrap

        if [[ $? == 0 ]]; then
            echo "INFO: CDK bootstrap completed successfully."
        else
            echo "ERROR: CDK bootstrap failed."
            exit 1
        fi

    else
        echo "INFO: CDK bootstrap stack already exists. Skipping..."
    fi

fi

if [[ $MODE == "deploy" ]]; then
    echo "INFO: Deploying infrastructure"
    cdk deploy
    echo "INFO: Finished deploying infrastructure"
elif [[ $MODE == "synth" ]]; then
    echo "INFO: Synthesizing infrastructure"
    cdk synth
    echo "INFO: Finished Synthesizing infrastructure"
elif [[ $MODE == "destroy" ]]; then
    echo "INFO: Destroying infrastructure"
    yes | cdk destroy
    echo "INFO: Finished destroying infrastructure"
else
    echo "ERROR: Invalid deployment mode: $MODE"
    exit 1
fi
