"""
This module provides code to fix errata/known problems with the GEOROC data.
"""
import math
import logging
import argparse
from typing import Protocol, Callable, Any, Literal, Union, TYPE_CHECKING, Optional

from pygeoroc.models import File, Sample

if TYPE_CHECKING:
    from .api import GEOROC

_log = None  # pylint: disable=C0103
ConverterType = Callable[[Any, dict[str, Any], str], Any]
LatLonType = Literal['latitude', 'longitude']


class Converters(Protocol):  # pylint: disable=R0903
    """A Python object with attributes specifying conversion logic."""
    COORDINATES: dict[str, dict[LatLonType, ConverterType]]
    FIELDS: dict[str, ConverterType]


def log() -> logging.Logger:
    """Initialize a logger."""
    global _log  # pylint: disable=W0603
    if _log is None:
        _log = logging.getLogger('georoc')
    return _log


def positive(val: Union[float, int], *_) -> float:
    """Make positive."""
    return math.copysign(val, 1)


def negative(val: Union[float, int], *_) -> float:
    """Make negative."""
    return math.copysign(val, -1)


CONVERTERS = argparse.Namespace(
    upper=lambda s, *_: s.upper(),
    positive=positive,
    negative=negative,
)


def fix(sample: Sample, f: File, api: 'GEOROC', stdout: Optional[bool] = False):
    """
    Fix the data of a sample.
    """
    def _fix(field, converter):
        new = converter(sample.data[field], sample.data, f.name)
        if new != sample.data[field]:
            msg = f'fixing {field} in {f.name}: {sample.data[field]} -> {new}'
            if stdout:
                print(msg)  # pragma: no cover
            elif stdout is None:  # pragma: no cover
                pass
            else:
                log().info(msg)
            sample.data[field] = new

    for field, conv in api.converters.FIELDS.items():
        if sample.data.get(field):
            _fix(field, conv)

    if f.name in api.converters.COORDINATES:
        for k in sample.data:
            prefix = k.split('_')[0].lower()
            if prefix in api.converters.COORDINATES[f.name] and sample.data[k]:
                _fix(k, api.converters.COORDINATES[f.name][prefix])
