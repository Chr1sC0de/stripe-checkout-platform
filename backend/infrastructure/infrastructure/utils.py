import os
import pathlib as pt

COMPANY = os.environ.get("COMPANY", "dummy-company")
ENVIRONMENT = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev")


def get_root_folder():
    return pt.Path(__file__).parents[1]
