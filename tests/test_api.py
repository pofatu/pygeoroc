
def test_samples(api):
    assert len(list(api.iter_samples())) == 426


def test_references(api):
    assert len(list(api.iter_references())) == 27
