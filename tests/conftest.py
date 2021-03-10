import shutil
import pathlib

import pytest

from pygeoroc import GEOROC


@pytest.fixture
def repos(tmp_path):
    p = tmp_path / 'repos'
    shutil.copytree(pathlib.Path(__file__).parent / 'repos', p)
    return p


@pytest.fixture
def api(repos):
    return GEOROC(repos)
