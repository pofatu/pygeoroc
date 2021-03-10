from pygeoroc.api import Sample, File
from pygeoroc.errata import fix


def test_fix_LAND_OR_SEA():
    sample = Sample(id='1', name='sample', citations='[1]', data=dict(LAND_OR_SEA='abc'))
    fix(sample, File('n', '2021-01-15', 'sec'))
    assert sample.data['LAND_OR_SEA'] == 'ABC'


def test_fix_coords():
    sample = Sample(
        id='1', name='sample', citations='[1]', data=dict(LATITUDE_MIN='12', LONGITUDE_MIN='-12'))
    fix(sample, File('Convergent_Margins_comp__NEW_CALEDONIA.csv', '2021-01-15', 'sec'))
    assert sample.data['LATITUDE_MIN'] < 0 and sample.data['LONGITUDE_MIN'] > 0
