#! /bin/bash

echo "INFO: Setting up the backend python environment ";

export source_folder=$(dirname -- "${BASH_SOURCE}");

cd "$source_folder/..";

# now create the python virtual environment if it does not exist

if [ -d ".venv" ]; then
    echo "INFO: .venv folder already exists, not creating";
else
    echo "INFO: .venv does not exist, creating";
    python -m venv .venv;
    echo "INFO: Finished creating .venv";
fi;

# activate the environment

echo "INFO: Activating .venv";
. .venv/bin/activate;
echo "INFO: Finisehd activating .venv";

echo "INFO: Installing pdm and ruff";
python -m pip install pdm;
python -m pip install ruff;
echo "INFO: Finished installing pdm and ruff";

echo "INFO: Installing infrastructure requirements"
cd ./backend/infrastructure;
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
echo "INFO: Finished installing infrastructure requirements"

echo "INFO: Finished setting up the backend python environment ";