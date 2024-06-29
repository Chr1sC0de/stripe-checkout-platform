#! /bin/bash

export source_folder=$(dirname -- "${BASH_SOURCE}");

# set the folder to the root directory

cd $source_folder/..;

# now create the python virtual environment if it does not exist

if [ -d ".venv" ]; then
    echo "INFO: .venv folder already exists, not creating";
else
    echo "INFO: .venv does not exist, creating";
    python -m venv .venv;
fi

# activate the environment

. .venv/bin/activate;

python -m pip install pdm;

# check what branch we are on and see if we can

export current_branch=$(git branch --show-current);

cd backend/infrastructure;

if [ $current_branch = "release" ]; then
    echo "INFO: in release branch not dev requirements installed"
    python -m pip install -r requirements.txt
else
    echo "INFO: in development environment all requirements installed"
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
fi;