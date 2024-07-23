#!/usr/bin/bash
: '
create a zip for the api library, this should be run after
    /scripts/initialize_backend_python_environment.sh
'

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder"/../backend/api-lib || exit

. .venv/bin/activate

rye sync

python -m pip install . -t lib

if [ -d dist ];
    then rm -rf dist
fi;

mkdir dist;

(cd lib || exit; zip ../dist/lambda.zip -r .);

zip dist/lambda.zip -u api.py;

chmod 775 dist/lambda.zip

rm -rf lib
