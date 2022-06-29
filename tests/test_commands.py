import json
import logging
import pathlib
import zipfile

import pytest
from clldutils.jsonlib import load

from pygeoroc.__main__ import main


@pytest.fixture
def _main(repos):
    def f(*args):
        return main(['--repos', str(repos)] + list(args), log=logging.getLogger(__name__))
    return f


def test_download(_main, caplog, repos, tmp_path):
    import requests_mock

    def content_callback(request, context):
        if 'access' in request.url:  # file download
            with zipfile.ZipFile(tmp_path / 'ds.zip', 'w') as zip:
                zip.write(
                    pathlib.Path(__file__).parent /
                    'repos' / 'csv' / '2022-06-1KRR1P_ZIMBABWE_CRATON_ARCHEAN.csv',
                    '2022-06-1KRR1P_ZIMBABWE_CRATON_ARCHEAN.csv')
            return tmp_path.joinpath('ds.zip').read_bytes()
        # Dataset metadata:
        return json.dumps(dict(data=load(repos / 'datasets.json')[0])).encode('utf8')

    with requests_mock.Mocker() as mock:
        mock.get(requests_mock.ANY, content=content_callback)

        caplog.set_level(logging.INFO)

        for p in repos.joinpath('csv').iterdir():
            p.unlink()

        _main('download')
        assert len(caplog.records) == 12
        _main('download')
        assert len(caplog.records) == 22


def test_createdb(_main, api, tmpdir):
    _main('createdb')
    assert api.dbpath.exists()
    res = api.dbquery('SELECT LATITUDE_MIN FROM sample WHERE LATITUDE_MIN < -19')
    assert len(res) == 376
    assert all(r['LATITUDE_MIN'] < -19 for r in res)
    _main('createdb')
    _main('createdb', '--force', '--archive', str(tmpdir))


def test_ls(_main, capsys):
    _main('ls', '--samples', '--references')
    out, _ = capsys.readouterr()
    assert 'Cratons' in out

    _main('ls', '--datasets-only')


def test_check(_main, capsys):
    _main('check')
    _, err = capsys.readouterr()
    assert not err
