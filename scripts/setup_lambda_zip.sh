#!/usr/bin/bash
: '
create a zip for a lambda library
'
target_folder=$1

echo $target_folder

if [[ -z $target_folder ]]; then
    echo "ERROR: target folder not set"
    exit
else
    echo "INFO: target lambda lib $target_folder"
fi

echo "INFO: Setting up lambda function"

if [[ -n $GITHUB_ACTIONS ]]; then
    source $HOME/.cargo/env
    source "$HOME/.rye/env"
fi

# shellcheck disable=SC2155
source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder"/../backend/api-lib || exit

rye sync

. .venv/bin/activate

echo "INFO: Creating zip"

python -m pip install . -t lib

if [ -d dist ]; then
    rm -rf dist
fi

mkdir dist

(
    cd lib || exit
    zip ../dist/lambda.zip -r .
)

rm -rf lib

echo "INFO: Finished creating zip"