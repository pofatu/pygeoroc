import logging
import sqlite3

import pytest

from pygeoroc.__main__ import main


@pytest.fixture
def _main(repos):
    def f(*args):
        return main(['--repos', str(repos)] + list(args), log=logging.getLogger(__name__))
    return f


def test_download(_main, mocker, caplog, repos):
    caplog.set_level(logging.INFO)
    downloads = """
<html>
<body>
<table id="tcompfiles" cellpadding="4">
	<tbody><tr>
		<td class="arialtbl" colspan="3" align="center">Archean Cratons </td>
	</tr><tr>
		<td class="arialtblk" align="left">Download</td>
		<td class="arialtblk" align="left">Size (KB)</td>
		<td class="arialtblk" align="left">Last Actualization</td>
	</tr><tr>
		<td class="arialtbl2"><a href="/georoc/Csv_Downloads/Archean_Cratons_comp/ZIMBABWE_CRATON_ARCHEAN.csv">ZIMBABWE CRATON ARCHEAN.csv</a></td>
		<td class="arialtbl2">208</td><td class="arialtbl2">3/9/2020</td>
	</tr></tbody></table></body></html>
"""

    class requests:
        def __init__(self, content=downloads):
            self.content = content

        def get(self, *args):
            return mocker.Mock(content=self.content)

    mocker.patch('pygeoroc.commands.download.requests', requests())
    _main('download')
    assert caplog.records

    mocker.patch(
        'pygeoroc.commands.download.requests', requests(downloads.replace('3/9/2020', '3/10/2020')))
    mocker.patch(
        'pygeoroc.commands.download.urlretrieve', mocker.Mock())
    _main('download')
    assert len(caplog.records) == 2

    repos.joinpath('csv', 'obsolete.csv').write_text('abc', encoding='utf8')
    _main('download')
    assert 'obsolete CSV files' in caplog.records[-1].msg
    _main('download', '--autoremove')
    assert 'obsolete' in caplog.records[-1].msg
    assert not repos.joinpath('csv', 'obsolete.csv').exists()


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

    _main('ls', '--sections-only')


def test_check(_main, capsys):
    _main('check')
    _, err = capsys.readouterr()
    assert not err
