from infrastructure.utils import get_root_folder


def test__get_root_folder():
    folder = get_root_folder()
    assert folder.name == "infrastructure"
