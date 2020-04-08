import shutil
import pathlib

import pytest

from pygeoroc import GEOROC


@pytest.fixture
def repos(tmpdir):
    p = pathlib.Path(str(tmpdir)) / 'repos'
    shutil.copytree(str(pathlib.Path(__file__).parent / 'repos'), str(p))
    return p


@pytest.fixture
def api(repos):
    return GEOROC(repos)
