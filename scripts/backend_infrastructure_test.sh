#! /bin/bash

echo "INFO: Testing Infrastructure"

# shellcheck disable=SC2155
export SOURCE_FOLDER="$(dirname -- "${BASH_SOURCE[0]}")"

. "$SOURCE_FOLDER/backend_infrastructure_set_env.sh"

cd "$SOURCE_FOLDER/.." || exit

cd ./backend/infrastructure || exit

. .venv/bin/activate

python -m pytest

if [[ $? ]]; then
    echo "INFO: Testing Passed"
else
    echo "ERROR: Testing Failed"
    exit 1
fi
