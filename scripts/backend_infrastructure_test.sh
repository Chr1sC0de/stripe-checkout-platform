#! /bin/bash

echo "INFO: Testing Infrastructure"

# shellcheck disable=SC2155
export SOURCE_FOLDER="$(dirname -- "${BASH_SOURCE[0]}")"

cd "$SOURCE_FOLDER/.." || exit

cd ./backend/infrastructure || exit

if ! [ -x "$(command -v cdk)" ]; then
    echo "INFO: No cdk command, installing"
    npm install -g aws-cdk
    echo "INFO: Finished installing cdk"
fi

cdk synth

pytest .

if [[ $? ]]; then
    echo "ERROR: Testing Failed";
    exit 1
else
    echo "INFO: Testing Passed";
fi
