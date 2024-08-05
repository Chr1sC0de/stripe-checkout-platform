#! /bin/bash

# ----------------------------- setup rye and uv ----------------------------- #

if ! [[ $(uv --help) ]]; then
    # to make things faster we can cache this installation at a later date
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

if ! [[ $(rye help) ]]; then
    # to make things faster we can cache this installation at a later date
    curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
    source "$HOME/.rye/env"
fi

echo "INFO: Setting Up the Backend Python Environment "

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder/.." || exit

echo "INFO: Setting Up Python Environment For Infrastructure"

cd "backend/infrastructure" || exit

if [[ -d ".venv" ]]; then
    echo "INFO: .venv Folder Already Exists, Not Creating"
else
    echo "INFO: .venv Does Not Exist, Creating"
    uv venv
    echo "INFO: Finished Creating .venv"
fi

echo "INFO: Activating .venv"
. .venv/bin/activate
echo "INFO: Finished Activating .venv"

echo "INFO: Installing Ruff"
uv pip install ruff
echo "INFO: Finished Installing Ruff"

echo "INFO: Installing Infrastructure Requirements"
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
echo "INFO: Finished installing Infrastructure Requirements"

echo "INFO: Finished Setting up Python Environment for Infrastructure"

deactivate

echo "INFO: Setting up Python Environment for API Library"

cd ../api-lib || exit

rye sync

echo "INFO: Finished up Python Environment for API Library"

echo "INFO: Finished setting up the backend python environment "
