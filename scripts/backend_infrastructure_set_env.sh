echo "INFO: Setting aws and service provider keys"

# shellcheck disable=SC2155
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