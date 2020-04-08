# pygeoroc

Python library to access data in the [GEOROC database](http://georoc.mpch-mainz.gwdg.de/georoc/Start.asp).

> Sarbas, B., U.Nohl: The GEOROC database as part of a growing geoinformatics network. In: Brady, S.R., Sinha, A.K., and Gundersen, L.C. (editors): Geoinformatics 2008—Data to Knowledge, Proceedings: U.S. Geological Survey Scientific Investigations Report 2008-5172 (2008), pp. 42/43.


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

GEOROC provides its [downloadable content](http://georoc.mpch-mainz.gwdg.de/georoc/CompFiles.aspx) in precompiled files organized in sections which correspond
mostly to locations.

`pygeoroc` provides functionality to
- download this data to a local directory, called *repository*,
- access the data in the repository programmatically from Python code,
- load the data from the repository into a SQLite database for scalable and
  performant analysis.
 

### Downloading GEOROC data

Downloading GEOROC data will create or update a local repository. Since the volume
of data provided per section differs greatly, downloading can be limited to individual
sections. E.g. running
```shell script
georoc --repos tmp/ download --section "Ocean Basin Flood Basalts"
```
will result in the following repository
```shell script
tree tmp/
tmp/
├── csv
│   ├── Ocean_Basin_Flood_Basalts_comp__ARGO_ABYSSAL_PLAIN;INDIAN_OCEAN.csv
│   ├── Ocean_Basin_Flood_Basalts_comp__EAST_MARIANA_BASIN.csv
│   ├── Ocean_Basin_Flood_Basalts_comp__NAURU_BASIN.csv
│   ├── Ocean_Basin_Flood_Basalts_comp__PIGAFETTA_BASIN.csv
│   └── Ocean_Basin_Flood_Basalts_comp__WHARTON_BASIN.csv
└── index.csv

1 directory, 6 files
```

Note that the repository also contains a "table of contents" in `index.csv`. The timestamp recorded per file in this table is checked against the "Last Actualization"
column on the web page to determine whether a file needs to be refreshed when `georoc download` is run again.

The local repository can be inspected running `georoc ls`, e.g.
```shell script
$ georoc --repos tmp/ ls --samples --references --format pipe
```
will output the table included below

| file | section | size | last modified | # samples | # references | path |
|:--------------------------------|:--------------------------|:--------|:----------------|------------:|---------------:|:----------------------------------------------------------------------------|
| ARGO_ABYSSAL_PLAIN;INDIAN_OCEAN | Ocean Basin Flood Basalts | 34.5KB | 2020-03-09 | 38 | 6 | tmp/csv/Ocean_Basin_Flood_Basalts_comp__ARGO_ABYSSAL_PLAIN;INDIAN_OCEAN.csv |
| EAST_MARIANA_BASIN | Ocean Basin Flood Basalts | 86.7KB | 2020-03-09 | 93 | 11 | tmp/csv/Ocean_Basin_Flood_Basalts_comp__EAST_MARIANA_BASIN.csv |
| NAURU_BASIN | Ocean Basin Flood Basalts | 273.9KB | 2020-03-09 | 356 | 18 | tmp/csv/Ocean_Basin_Flood_Basalts_comp__NAURU_BASIN.csv |
| PIGAFETTA_BASIN | Ocean Basin Flood Basalts | 349.0KB | 2020-03-09 | 428 | 18 | tmp/csv/Ocean_Basin_Flood_Basalts_comp__PIGAFETTA_BASIN.csv |
| WHARTON_BASIN | Ocean Basin Flood Basalts | 75.7KB | 2020-03-09 | 94 | 8 | tmp/csv/Ocean_Basin_Flood_Basalts_comp__WHARTON_BASIN.csv |


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