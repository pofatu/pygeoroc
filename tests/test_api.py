
def test_samples(api):
    samples = list(api.iter_samples())
    assert len(samples) == 426
    sample, f = samples[0]
    assert 'ELEVATION_MAX' in sample.data
    assert sample.region == 'ZIMBABWE CRATON_ARCHEAN'
    assert f.name == 'Archean_Cratons_comp__ZIMBABWE_CRATON_ARCHEAN.csv'


def test_references(api):
    assert len(list(api.iter_references())) == 27
