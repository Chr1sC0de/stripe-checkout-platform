#!/usr/bin/bash
: '
create a zip for the api library, this should be run after
    /scripts/initialize_backend_python_environment.sh
'

echo "INFO: Setting up lambda function"

if [[ -n $GITHUB_ACTIONS ]]; then
    source $HOME/.cargo/env
    source "$HOME/.rye/env"
fi

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder"/../backend/api-lib || exit

. .venv/bin/activate

rye sync

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

zip dist/lambda.zip -u api.py

chmod 775 dist/lambda.zip

rm -rf lib

echo "INFO: Finished creating zip"

deactivate

cd $source_folder/.. || exit

echo "INFO: Finished setting up lambda function"