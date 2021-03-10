"""
This module provides code to fix errata/known problems with the GEOROC data.
"""
import math
import logging

_log = None


def log():
    global _log
    if _log is None:
        _log = logging.getLogger('georoc')
    return _log


def positive(val):
    return math.copysign(val, 1)


def negative(val):
    return math.copysign(val, -1)


COORDINATES = {
    "Convergent_Margins_comp__BISMARCK_ARC_-_NEW_BRITAIN_ARC.csv": {
        'latitude': negative, 'longitude': positive
    },
    "Convergent_Margins_comp__IZU-BONIN_ARC.csv": {
        'latitude': positive,
        'longitude': positive
    },
    "Convergent_Margins_comp__KERMADEC_ARC.csv": {
        'latitude': negative,
    },
    "Convergent_Margins_comp__LUZON_ARC.csv": {
        'longitude': positive
    },
    "Convergent_Margins_comp__MARIANA_ARC.csv": {
        'latitude': positive,
        'longitude': positive

    },
    "Convergent_Margins_comp__NEW_CALEDONIA.csv": {
        'latitude': negative,
        'longitude': positive
    },
    # "Convergent_Margins_comp__NEW_CALEDONIA.csv"
    # and "LOCATION" = "NEW CALEDONIA / NEW CALEDONIA / POYA TERRANE"
    # longitudes should be 163.0000 (instead of -21.0000)
    "Convergent_Margins_comp__NEW_HEBRIDES_ARC_-_VANUATU_ARCHIPELAGO.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Convergent_Margins_comp__NEW_ZEALAND.csv": {
        'latitude': negative,
        'longitude': positive
    },
    "Convergent_Margins_comp__SOLOMON_ISLAND_ARC.csv": {
        'latitude': negative,
        'longitude': positive
    },
    "Convergent_Margins_comp__SULAWESI_ARC.csv": {
        'longitude': positive
    },
    "Convergent_Margins_comp__TONGA_ARC.csv": {
        'latitude': negative,
    },
    "Convergent_Margins_comp__YAP_ARC.csv": {
        'latitude': positive,
        # longitudes are generally positive except when LOCATION includes
        # "TONGA ARC / FIJI ISLANDS" or "TONGA ARC / LAU BASIN"
    },
    "Ocean_Island_Groups_comp__AUSTRAL-COOK_ISLANDS.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__CAROLINE_ISLANDS.csv": {
        'latitude': positive,
        'longitude': positive
    },
    "Ocean_Island_Groups_comp__EASTER_SEAMOUNT_CHAIN_-_SALAS_Y_GOMEZ_RIDGE.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__PITCAIRN-GAMBIER_CHAIN.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__HAWAIIAN_ISLANDS_part1.csv": {
        'latitude': positive,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__HAWAIIAN_ISLANDS_part2.csv": {
        'latitude': positive,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__HAWAIIAN-EMPEROR_CHAIN.csv": {
        'latitude': positive,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__HAWAIIAN_ARCH_VOLCANIC_FIELDS.csv": {
        'latitude': positive,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__SOCIETY_ISLANDS.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Seamounts_comp__s_SAMOAN_ISLANDS.csv": {
        'latitude': negative,
        'longitude': negative
    },
    "Ocean_Island_Groups_comp__SAMOAN_ISLANDS.csv": {
        'latitude': negative,
        'longitude': negative
    },
}


def fix(sample, f):
    """
    :param data: A `dict` representing the data of a row in a GEOROC CSV file.
    :return: The `dict` with corrected data.
    """
    if sample.data.get('LAND_OR_SEA'):
        upper = sample.data['LAND_OR_SEA'].upper()
        if sample.data['LAND_OR_SEA'] != upper:
            log().info('fixing {} in {}: {} -> {}'.format(
                'LAND_OR_SEA', f.name, sample.data['LAND_OR_SEA'], upper))
            sample.data['LAND_OR_SEA'] = upper

    if f.name in COORDINATES:
        for k in sample.data:
            prefix = k.split('_')[0].lower()
            if prefix in COORDINATES[f.name] and sample.data[k]:
                new = COORDINATES[f.name][prefix](sample.data[k])
                if new != sample.data[k]:
                    log().info('fixing {} in {}: {} -> {}'.format(k, f.name, sample.data[k], new))
                    sample.data[k] = new
