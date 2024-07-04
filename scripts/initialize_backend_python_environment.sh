#! /bin/bash

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

echo "INFO: Setting up the backend python environment "

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder/.." || exit

echo "Setting up Python Environment for Infrastructure"

cd "backend/infrastructure" || exit

if [[ -d ".venv" ]]; then
    echo "INFO: .venv folder already exists, not creating"
else
    echo "INFO: .venv does not exist, creating"
    uv venv
    echo "INFO: Finished creating .venv"
fi

echo "INFO: Activating .venv"
. .venv/bin/activate
echo "INFO: Finisehd activating .venv"

echo "INFO: and ruff"
uv pip install ruff
echo "INFO: Finished installing pdm and ruff"

echo "INFO: Installing infrastructure requirements"
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
echo "INFO: Finished installing infrastructure requirements"

echo "Finished Setting up Python Environment for Infrastructure"

echo "INFO: Finished setting up the backend python environment "
