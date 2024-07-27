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

cd "$target_folder" || exit

rye sync -f

# . .venv/bin/activate

echo "INFO: Creating zip"

# python -m pip install . -t lib

if [ -d dist ]; then
    rm -rf dist
fi

if [ -d lib ]; then
    rm -rf lib
fi

mkdir dist

echo "INFO: Moving site-packages to lib"
cp -r .venv/lib/python*/site-packages lib || exit
echo "INFO: Finished moving site-packages to lib"

echo "INFO: Copying main package to lib"
cp -r src/* -t lib || exit
echo "INFO: Finished copying main package to lib"

echo "INFO: Zipping lib"
(
    cd lib || exit
    zip ../dist/lambda.zip -r . -1 -q
)
echo "INFO: Finished zipping lib"

rm -rf lib

echo "INFO: Finished creating zip"