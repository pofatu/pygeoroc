
def test_samples(api):
    assert len(list(api.iter_samples())) == 426
