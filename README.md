# pygeoroc

[![Build Status](https://github.com/pofatu/pygeoroc/workflows/tests/badge.svg)](https://github.com/pofatu/pygeoroc/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/pofatu/pygeoroc/branch/master/graph/badge.svg)](https://codecov.io/gh/pofatu/pygeoroc)
[![PyPI](https://img.shields.io/pypi/v/pygeoroc.svg)](https://pypi.org/project/pygeoroc)


Python library to access data in the [GEOROC data](https://georoc.eu/georoc/new-start.asp) as archived at
https://data.goettingen-research-online.de/dataverse/digis.

Cite GEOROC data as specified 
[for each pre-compiled dataset](https://data.goettingen-research-online.de/dataverse/digis?q=&types=datasets&sort=dateSort&order=desc&page=1)
and `pygeoroc` as

> Robert Forkel. (2022). pofatu/pygeoroc: Programmatic access to GEOROC data. Zenodo. http://doi.org/10.5281/zenodo.3744586


## Install

Install `pygeoroc` from the [Python Package Index](https://pypi.org) running
```shell script
pip install pygeoroc
```
preferably in a separate [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/), to keep your system's Python installation unaffected.

Installing `pygeoroc` will also install a command line program `georoc`, which provides
functionality to curate a local copy of the GEOROC data. Run
```shell script
georoc -h
```
for details on usage.


## Overview

GEOROC provides its downloadable content in precompiled files organized in datasets.

`pygeoroc` provides functionality to
- download this data to a local directory, called *repository*,
- access the data in the repository programmatically from Python code,
- load the data from the repository into a SQLite database for scalable and
  performant analysis.
 

### Downloading GEOROC data

Downloading GEOROC data will create or update a local repository, i.e. a directory with the following layout:
```shell
$ tree -L 1 .
.
├── csv
└── datasets.json
```

The repository contains a "table of contents" in `datasets.json`. The checksum recorded per file in this table is checked
when running `georoc download` again, making sure only new versions of files are fetched.

The local repository can be inspected running `georoc ls`, e.g.
```shell script
$ georoc --repos tmp/ ls --samples --references --format pipe
```
will output the table included below

| file | dataset | size | last modified | # samples | # references | path |
|:---------------------------------------------------------------------|:----------------------------------------------|:---------|:----------------|------------:|---------------:|:------------------------------------------------------------------------------------------|
| [doi:10.25625/1KRR1P/QIINIE](https://doi.org/10.25625/1KRR1P/QIINIE) | GEOROC Compilation: Archaean Cratons | 211.7KB | 2022-06-20 | 242 | 8 | 2022-06-1KRR1P_ALDAN_SHIELD_ARCHEAN.csv |
| [doi:10.25625/1KRR1P/9YG7VJ](https://doi.org/10.25625/1KRR1P/9YG7VJ) | GEOROC Compilation: Archaean Cratons | 494.3KB | 2022-06-20 | 564 | 23 | 2022-06-1KRR1P_AMAZONIAN_CRATON.csv |
| [doi:10.25625/1KRR1P/E7NI47](https://doi.org/10.25625/1KRR1P/E7NI47) | GEOROC Compilation: Archaean Cratons | 3.3MB | 2022-06-20 | 3776 | 66 | 2022-06-1KRR1P_BALTIC_SHIELD_ARCHEAN.csv |
| [doi:10.25625/1KRR1P/FY7PXY](https://doi.org/10.25625/1KRR1P/FY7PXY) | GEOROC Compilation: Archaean Cratons | 53.8KB | 2022-06-20 | 61 | 5 | 2022-06-1KRR1P_BASTAR_CRATON_ARCHEAN.csv |

...


### Loading GEOROC data into SQLite

Since GEOROC contains data about hundreds of thousands of samples, querying it
is made a lot easier by loading it into a SQLite database:
```shell script
$ georoc --repos tmp/ createdb
100%|██████████████████████████████████████████████████| 5/5 [00:00<00:00, 25.32it/s]
INFO    tmp/georoc.sqlite
```

The resulting database has 4 tables:
- `file`: Info about a CSV file, basically the data from `index.csv`.
- `sample`: Info about individual samples.
- `reference`: Info about sources of the data
- `citation`: The association table relating samples with references.

The schema can be inspected running:
```shell script
$ sqlite3 tmp/georoc.sqlite
SQLite version 3.11.0 2016-02-15 17:29:24
Enter ".help" for usage hints.
sqlite> .schema
```
and looks as follows:
```sql
CREATE TABLE file (id TEXT PRIMARY KEY, date TEXT, section TEXT);
CREATE TABLE reference (id INTEGER PRIMARY KEY, reference TEXT);
CREATE TABLE sample (
    id TEXT PRIMARY KEY,
    file_id TEXT,
    `AGE` TEXT,
`ALTERATION` TEXT,
`DRILL_DEPTHAX` TEXT,
`DRILL_DEPTH_MIN` TEXT,
`ELEVATION_MAX` TEXT,
`ELEVATION_MIN` TEXT,
`EPSILON_ND` TEXT,
`ERUPTION_DAY` TEXT,
`ERUPTION_MONTH` TEXT,
`ERUPTION_YEAR` TEXT,
`GEOL.` TEXT,
`LAND_OR_SEA` TEXT,
`LATITUDE_MAX` TEXT,
`LATITUDE_MIN` TEXT,
`LOCATION` TEXT,
`LOCATION_COMMENT` TEXT,
`LONGITUDE_MAX` TEXT,
`LONGITUDE_MIN` TEXT,
`MATERIAL` TEXT,
`MINERAL` TEXT,
`ROCK_NAME` TEXT,
`ROCK_TEXTURE` TEXT,
`ROCK_TYPE` TEXT,
`TECTONIC_SETTING` TEXT,
`AR40_K40` TEXT,
`HE3_HE4` TEXT,
`HE4_HE3` TEXT,
`HF176_HF177` TEXT,
`K40_AR40` TEXT,
`ND143_ND144` TEXT,
`ND143_ND144_INI` TEXT,
`OS184_OS188` TEXT,
`OS186_OS188` TEXT,
`OS187_OS186` TEXT,
`OS187_OS188` TEXT,
`PB206_PB204` TEXT,
`PB206_PB204_INI` TEXT,
`PB207_PB204` TEXT,
`PB207_PB204_INI` TEXT,
`PB208_PB204` TEXT,
`PB208_PB204_INI` TEXT,
`RE187_OS186` TEXT,
`RE187_OS188` TEXT,
`SR87_SR86` TEXT,
`SR87_SR86_INI` TEXT,
`AG(PPM)` TEXT,
`AL(PPM)` TEXT,
`AS(PPM)` TEXT,
`AU(PPM)` TEXT,
`B(PPM)` TEXT,
`BA(PPM)` TEXT,
`BE(PPM)` TEXT,
`BI(PPM)` TEXT,
`BR(PPM)` TEXT,
`C(PPM)` TEXT,
`CA(PPM)` TEXT,
`CAO(WT%)` TEXT,
`CD(PPM)` TEXT,
`CE(PPM)` TEXT,
`CL(PPM)` TEXT,
`CL(WT%)` TEXT,
`CO(PPM)` TEXT,
`CR(PPM)` TEXT,
`CS(PPM)` TEXT,
`CU(PPM)` TEXT,
`DY(PPM)` TEXT,
`ER(PPM)` TEXT,
`EU(PPM)` TEXT,
`F(PPM)` TEXT,
`F(WT%)` TEXT,
`FE(PPM)` TEXT,
`FEO(WT%)` TEXT,
`FEOT(WT%)` TEXT,
`GA(PPM)` TEXT,
`GD(PPM)` TEXT,
`GE(PPM)` TEXT,
`HE(CCM/G)` TEXT,
`HE(CCMSTP/G)` TEXT,
`HE(NCC/G)` TEXT,
`HF(PPM)` TEXT,
`HG(PPM)` TEXT,
`HO(PPM)` TEXT,
`I(PPM)` TEXT,
`IN(PPM)` TEXT,
`IR(PPM)` TEXT,
`K(PPM)` TEXT,
`LA(PPM)` TEXT,
`LI(PPM)` TEXT,
`LOI(WT%)` TEXT,
`LU(PPM)` TEXT,
`MAX._AGE_(YRS.)` TEXT,
`MG(PPM)` TEXT,
`MGO(WT%)` TEXT,
`MIN._AGE_(YRS.)` TEXT,
`MN(PPM)` TEXT,
`MNO(WT%)` TEXT,
`MO(PPM)` TEXT,
`NA(PPM)` TEXT,
`NB(PPM)` TEXT,
`ND(PPM)` TEXT,
`NI(PPM)` TEXT,
`NIO(WT%)` TEXT,
`O(WT%)` TEXT,
`OH(WT%)` TEXT,
`OS(PPM)` TEXT,
`OTHERS(WT%)` TEXT,
`P(PPM)` TEXT,
`PB(PPM)` TEXT,
`PD(PPM)` TEXT,
`PR(PPM)` TEXT,
`PT(PPM)` TEXT,
`RB(PPM)` TEXT,
`RE(PPM)` TEXT,
`RH(PPM)` TEXT,
`RU(PPM)` TEXT,
`S(PPM)` TEXT,
`S(WT%)` TEXT,
`SB(PPM)` TEXT,
`SC(PPM)` TEXT,
`SE(PPM)` TEXT,
`SM(PPM)` TEXT,
`SN(PPM)` TEXT,
`SR(PPM)` TEXT,
`TA(PPM)` TEXT,
`TB(PPM)` TEXT,
`TE(PPM)` TEXT,
`TH(PPM)` TEXT,
`TI(PPM)` TEXT,
`TL(PPM)` TEXT,
`TM(PPM)` TEXT,
`U(PPM)` TEXT,
`V(PPM)` TEXT,
`VOLATILES(WT%)` TEXT,
`W(PPM)` TEXT,
`Y(PPM)` TEXT,
`YB(PPM)` TEXT,
`ZN(PPM)` TEXT,
`ZR(PPM)` TEXT,
`AL2O3(WT%)` TEXT,
`B2O3(WT%)` TEXT,
`CH4(WT%)` TEXT,
`CL2(WT%)` TEXT,
`CO1(WT%)` TEXT,
`CO2(PPM)` TEXT,
`CO2(WT%)` TEXT,
`CR2O3(WT%)` TEXT,
`FE2O3(WT%)` TEXT,
`H2O(WT%)` TEXT,
`H2OM(WT%)` TEXT,
`H2OP(WT%)` TEXT,
`H2OT(WT%)` TEXT,
`HE3(AT/G)` TEXT,
`HE3(CCMSTP/G)` TEXT,
`HE3_HE4(R/R(A))` TEXT,
`HE4(AT/G)` TEXT,
`HE4(CCM/G)` TEXT,
`HE4(CCMSTP/G)` TEXT,
`HE4(MOLE/G)` TEXT,
`HE4(NCC/G)` TEXT,
`HE4_HE3(R/R(A))` TEXT,
`K2O(WT%)` TEXT,
`NA2O(WT%)` TEXT,
`P2O5(WT%)` TEXT,
`SIO2(WT%)` TEXT,
`SO2(WT%)` TEXT,
`SO3(WT%)` TEXT,
`SO4(WT%)` TEXT,
`TIO2(WT%)` TEXT,
    FOREIGN KEY (file_id) REFERENCES file(id)
);
CREATE TABLE citation (
    sample_id TEXT,
    reference_id INTEGER,
    FOREIGN KEY (sample_id) REFERENCES sample(id),
    FOREIGN KEY (reference_id) REFERENCES reference(id)
);
```

Thus, information similar to what is reported by `georoc ls` can be obtained by
running SQL queries.

E.g. to determine the paper which contributed the highest number of samples in the
"Ocean Basin Flood Basalts" section, we can run
```sql
SELECT
    r.reference, COUNT(c.sample_id) AS c
FROM
    reference as r, citation as c
WHERE
    r.id = c.reference_id
GROUP BY r.reference
ORDER BY c DESC
LIMIT 1;
```
which yields
```
KELLEY KATHERINE A., PLANK T. A., LUDDEN J. N., STAUDIGEL H.:    COMPOSITION OF ALTERED OCEANIC CRUST AT ODP SITES 801 AND 1149  GEOCHEMISTRY GEOPHYSICS GEOSYSTEMS 4   [2003]    GeoReM-id: 305   doi: 10.1029/2002GC000435|123
```


### Accessing GEOROC data programmatically

`pygeoroc` provides a Python API to access local GEOROC data:
```python
>>> from pygeoroc import GEOROC
>>> api = GEOROC('tmp/')
>>> for sample in api.iter_samples():
>>> for sample, file in api.iter_samples():
...     print(sample)
...     print(file)
...     break
... 
Sample(id='138180', name='s_27-261-33,CC,PC. 2 [2118]', citations=['2118'], data={'SR(PPM)': '', ... })
File(name='Ocean_Basin_Flood_Basalts_comp__ARGO_ABYSSAL_PLAIN;INDIAN_OCEAN.csv', date=datetime.date(2020, 3, 9), section='Ocean Basin Flood Basalts')
```


### Converters

For both access modes - SQLite and the python API - `pygeoroc` provides a
mechanism to specify "converters", i.e. python callables to convert the values
for specific columns in GEOROC CSV data. This mechanism can be used to fix
errata - e.g. missing negative signs in geographic coordinates - or cast data
to more suitable datatypes.

This mechanism is implemented in [`pygeoroc.errata`](src/pygeoroc/errata.py)
and works as follows: If the data repository contains a python module called
`converters.py`, this module is loaded and two python `dict`s are looked up
by name:
- `FIELDS`: `dict` mapping CSV column names to converter functions.
- `COORDINATES`: `dict` mapping CSV filenames (as stored in the repository)
  to `dict`s specifying converter functions for keys `latitude` and `longitude`.
  
A "converter function" is a python callable with the following signature:
```python
def conv(old, data, fname):
    """
    @param old: old value for the respective field in the sample data
    @param data: full `dict` of the sample data in one row in the GEOROC CSV
    @param fname: name of the GEOROC CSV file containing the row
    @return: the new value for "field" in "data"
    """
```

Some useful converter functions are available as attributes of 
[`pygeoroc.errata.CONVERTERS`](src/pygeoroc/errata.py).

So, to specify that values for the column `LAND_OR_SEA` must be all uppercase,
and latitudes in the file `Convergent_Margins_comp__BISMARCK_ARC_-_NEW_BRITAIN_ARC.csv`
must be negative, you would put the following python code in your repository's
`converters.py`:
```python
from pygeoroc.errata import CONVERTERS

FIELDS = {
    'LAND_OR_SEA': CONVERTERS.upper,
}

COORDINATES = {
    "Convergent_Margins_comp__BISMARCK_ARC_-_NEW_BRITAIN_ARC.csv": {
        'latitude': CONVERTERS.negative,
    },
}
```