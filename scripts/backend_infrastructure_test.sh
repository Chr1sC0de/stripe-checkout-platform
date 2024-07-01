#! /bin/bash

echo "INFO: Testing Infrastructure"

# shellcheck disable=SC2155
export SOURCE_FOLDER="$(dirname -- "${BASH_SOURCE[0]}")"

. "$SOURCE_FOLDER/backend_infrastructure_set_env.sh"

cd "$SOURCE_FOLDER/.." || exit

cd ./backend/infrastructure || exit

python -m pytest

if [[ $? ]]; then
    echo "ERROR: Testing Failed";
    exit 1
else
    echo "INFO: Testing Passed";
fi
