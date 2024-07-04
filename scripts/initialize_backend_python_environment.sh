#! /bin/bash

if ! [[ $(uv --help) ]];
then
    # to make things faster we can cache this installation
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! [[ $(rye help ) ]];
then
    # to make things faster we can cache this installation
    curl -sSf https://rye.astral.sh/get | bash
    source "$HOME/.rye/env"
fi

echo "INFO: Setting up the backend python environment ";

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}");

cd "$source_folder/.." || exit;

# now create the python virtual environment if it does not exist

if [[ -d ".venv" ]]; then
    echo "INFO: .venv folder already exists, not creating";
else
    echo "INFO: .venv does not exist, creating";
    uv venv;
    echo "INFO: Finished creating .venv";
fi;

# activate the environment

echo "INFO: Activating .venv";
. .venv/bin/activate;
echo "INFO: Finisehd activating .venv";

echo "INFO: and ruff";
uv pip install ruff;
echo "INFO: Finished installing pdm and ruff";

echo "INFO: Installing infrastructure requirements"
cd ./backend/infrastructure || exit;
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
echo "INFO: Finished installing infrastructure requirements"

echo "INFO: Finished setting up the backend python environment ";