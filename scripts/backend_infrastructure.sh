#! /bin/bash

if [[ -d ~/.aws/config ]]; then
    rm ~/.aws/config
fi

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder/.." || exit

. "$source_folder/backend_infrastructure_set_env.sh"
(. "$source_folder/setup_lambda_zip.sh")

echo "INFO: The current aws cli version is: $(aws --version)"
echo "INFO: The current npm version is: $(npm --version)"

if ! [ -x "$(command -v cdk)" ]; then
    echo "INFO: No cdk command, installing"
    npm install -g aws-cdk
    echo "INFO: Finished installing cdk"
fi

echo "INFO: The current cdk version is: $(cdk --version)"

cd ./backend/infrastructure || exit

. .venv/bin/activate

# bootstrap the environment if it has not been run before

if [[ $MODE != 'synth' ]]; then

    echo "INFO: Checking if Bootstrap exists"

    # shellcheck disable=SC2155
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
    cdk deploy --all
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
