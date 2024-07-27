#!/usr/bin/bash
: '
create a zip for the api library, this should be run after
    /scripts/initialize_backend_python_environment.sh
'
# shellcheck disable=SC2155
source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder"/.. || exit

(scripts/setup_lambda_zip.sh backend/api-lib/) || exit

echo "INFO: Adding api to lambda zip"

cd backend/api-lib || exit

zip dist/lambda.zip -u api.py

chmod 775 dist/lambda.zip

echo "INFO: Finished adding api to lambda zip"