from pygeoroc.errata import CONVERTERS

FIELDS = {
    'LAND_OR_SEA': CONVERTERS.upper,
}

COORDINATES = {
    'Convergent_Margins_comp__NEW_CALEDONIA.csv': {
        'latitude': CONVERTERS.negative,
        'longitude': CONVERTERS.positive,
    }
}
