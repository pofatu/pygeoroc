from types import SimpleNamespace

from pygeoroc.api import Sample
from pygeoroc.errata import fix


def test_fix_LAND_OR_SEA(api, mocker):
    sample = Sample(id='1', name='sample', citations='[1]', data=dict(LAND_OR_SEA='abc'))
    fix(sample, mocker.Mock(), api)
    assert sample.data['LAND_OR_SEA'] == 'ABC'


def test_fix_coords(api, mocker):
    sample = Sample(
        id='1', name='sample', citations='[1]', data=dict(LATITUDE_MIN='12', LONGITUDE_MIN='-12'))
    fix(sample, SimpleNamespace(name='NEW_CALEDONIA.csv'), api)
    assert sample.data['LATITUDE_MIN'] < 0 and sample.data['LONGITUDE_MIN'] > 0
