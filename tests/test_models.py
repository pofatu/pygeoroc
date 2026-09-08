import pytest

from pygeoroc.models import value_and_refs


@pytest.mark.parametrize(
    's,value,refs',
    [
        ('', '', set()),
        ('[1]', '', {'1'}),
        ('x [1]', 'x', {'1'}),
        ('x', 'x', set()),
        ('[2] x [1]', 'x', {'1', '2'}),
    ]
)
def test_value_and_refs(s, value, refs):
    assert value_and_refs(s) == (value, refs)

