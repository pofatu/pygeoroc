# Contributing to pygeoroc

## Installing pygeoroc for development

1. Fork `pofatu/pygeoroc`
2. Clone your fork
3. Install `pygeoroc` for development (preferably in a separate [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)) running
```shell script
pip install -r requirements
```

## Running the test suite

The test suite is run via

```shell script
pytest
```

Cross-platform compatibility tests can additionally be run via
```shell script
tox -r
```

