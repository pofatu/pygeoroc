"""
This module provides code to fix errata/known problems with the GEOROC data.
"""
import math
import logging
import argparse

_log = None


def log():
    global _log
    if _log is None:
        _log = logging.getLogger('georoc')
    return _log


def positive(val, *_):
    return math.copysign(val, 1)


def negative(val, *_):
    return math.copysign(val, -1)


CONVERTERS = argparse.Namespace(
    upper=lambda s, *_: s.upper(),
    positive=positive,
    negative=negative,
)


def fix(sample, f, api, stdout=False):
    """
    :param data: A `dict` representing the data of a row in a GEOROC CSV file.
    :return: The `dict` with corrected data.
    """
    def _fix(field, converter):
        new = converter(sample.data[field], sample.data, f.name)
        if new != sample.data[field]:
            msg = 'fixing {} in {}: {} -> {}'.format(field, f.name, sample.data[field], new)
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
