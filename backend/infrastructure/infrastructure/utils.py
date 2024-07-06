import os
import pathlib as pt

COMPANY = os.environ.get("COMPANY", "my-test-company-name")
DEVELOPMENT_ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev")


def get_root_folder():
    return pt.Path(__file__).parents[1]
