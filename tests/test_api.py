
def test_dataset(api):
    assert 'DIGIS' in api.index[0].citation


def test_samples(api):
    samples = list(api.iter_samples())
    assert len(samples) == 426
    sample, f = samples[0]
    assert 'ELEVATION_MAX' in sample.data
    assert sample.region == 'ZIMBABWE CRATON_ARCHEAN'


def test_references(api):
    assert len(list(api.iter_references())) == 27
