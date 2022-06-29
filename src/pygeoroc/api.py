import io
import re
import typing
import pathlib
import sqlite3
import zipfile
import argparse
import itertools
import contextlib
import collections

import requests
from clldutils.apilib import API
from clldutils.misc import lazyproperty
from clldutils.path import md5
from clldutils.jsonlib import update, dump
from csvw import dsv
import attr

# DIGIS Dataverse API:
API_URL = "https://data.goettingen-research-online.de/api/"

# We exclude files in redundant sections of the precompilations when iterating over samples:
COL_MAP = {
    'ELEVATION_(MAX.)': 'ELEVATION_MAX',
    'ELEVATION_(MIN.)': 'ELEVATION_MIN',
    'LATITUDE_(MAX.)': 'LATITUDE_MAX',
    'LATITUDE_(MIN.)': 'LATITUDE_MIN',
    'LONGITUDE_(MAX.)': 'LONGITUDE_MAX',
    'LONGITUDE_(MIN.)': 'LONGITUDE_MIN',
}
CITATION_PATTERN = re.compile(r'\[(?P<ref>[0-9]+)]')


def api_call(p):
    assert not p.startswith('/')
    return requests.get('{}{}'.format(API_URL, p))


class File:
    """
    Represents one file in a dataset from dataverse.
    """
    def __init__(self, md: dict, section: typing.Optional[str] = None):
        self.md = md
        self.section = section
        self.name = self.md['filename']
        assert self.name == self.name.strip()
        self.path = pathlib.Path(self.name)
        self.date = self.md['creationDate']
        self.md5 = self.md['md5']
        self.size = self.md['filesize']
        self.id = self.md['persistentId']

    def exists(self, repos: 'GEOROC') -> bool:
        """
        Checks whether the specified file exists with correct checksum in the repository.
        """
        p = repos.csvdir / self.name
        return p.exists() and md5(p) == self.md5

    def iter_lines(self, repos: 'GEOROC') -> typing.Generator[str, None, None]:
        for line in repos.csvdir.joinpath(self.name).open(encoding='cp1252'):
            if line.strip():
                yield line.strip()

    def iter_samples(self, repos: 'GEOROC', stdout=False) -> typing.Generator['Sample', None, None]:
        from pygeoroc import errata
        lines = itertools.takewhile(
            lambda l: not (l.startswith('Abbreviations') or l.startswith('References:')),
            self.iter_lines(repos))
        for i, row in enumerate(dsv.reader(lines, dicts=True), start=2):
            try:
                sample = Sample.from_row(row)
            except:  # pragma: no cover # noqa: E722
                print('{}:{}'.format(self.name, i))
                raise
            errata.fix(sample, self, repos, stdout=stdout)
            yield sample

    def iter_references(
            self, repos: 'GEOROC') -> typing.Generator[typing.Tuple[int, str], None, None]:
        in_refs = False
        for line in self.iter_lines(repos):
            if in_refs:
                if line.startswith('"'):
                    line = line[1:].strip()
                if line.endswith('"'):
                    line = line[:-1].strip()
                m = re.match(r'\[(?P<id>[0-9]+)]\s+(?P<ref>.+)', line)
                if m:
                    yield int(m.group('id')), m.group('ref')

            if line.startswith('References:'):
                in_refs = True


class Dataset:
    def __init__(self, md: dict):
        self.md = md
        self.doi = '{}:{}/{}'.format(
            self.md['protocol'], self.md['authority'], self.md['identifier'])
        self._citation_data = {
            f['typeName']: f['value'] for f in
            self.md['latestVersion']['metadataBlocks']['citation']['fields']}
        self.name = self._citation_data['title']

    @classmethod
    def from_doi(cls, doi: str) -> 'Dataset':
        return cls(api_call('datasets/:persistentId/?persistentId=' + doi).json()['data'])

    @property
    def citation(self) -> str:
        res = ' and '.join([v['authorName']['value'] for v in self._citation_data['author']])
        res += ', {}, '.format(self._citation_data['dateOfDeposit'].split('-')[0])
        res += '"{}", '.format(self._citation_data['title'])
        res += '{}, '.format(self.md['persistentUrl'])
        res += '{}, '.format(self.md['publisher'])
        res += 'V{}'.format(self.md['latestVersion']['versionNumber'])
        return res

    @property
    def files(self) -> typing.List[File]:
        return [File(r['dataFile'], section=self.name) for r in self.md['latestVersion']['files']]

    def download_files(self, repos: 'GEOROC', log=None):
        # Check, whether we have to download any files:
        missing = {f.name for f in self.files if not f.exists(repos)}
        print(missing)
        if missing:
            if log:
                log.info('Downloading files for dataset "{}" ...'.format(self.name))
            r = api_call('access/dataset/:persistentId/?persistentId={}'.format(self.doi))
            z = zipfile.ZipFile(io.BytesIO(r.content))
            if log:
                log.info('... done')
            for name in z.namelist():
                assert name == name.strip()
                if name in missing:
                    if log:
                        log.info('Updating file {}'.format(name))
                    repos.csvdir.joinpath(name).write_bytes(z.read(name))
        else:
            if log:
                log.info(
                    'Skipping download for dataset "{}". All files up-to-date.'.format(self.name))


def col_type(s):
    if s in [
        'MIN._AGE_(YRS.)',  # '3480000000  / 3484000000'
        'MAX._AGE_(YRS.)',  # '3480000000  / 3484000000'
    ]:
        return str
    if s in COL_MAP.values():
        return float
    if '(' in s:
        return float
    if '_' in s and re.search(r'[0-9]', s):
        return float
    return str


def value_and_refs(v):
    refs = set()

    def repl(m):
        refs.add(m.group('ref'))
        return ''

    return CITATION_PATTERN.sub(repl, v).strip(), refs


def citations_converter(s):
    v, res = value_and_refs(s)
    assert not v
    return collections.OrderedDict([(k, []) for k in res])


@attr.s
class Sample:
    id = attr.ib()
    name = attr.ib()
    citations = attr.ib(converter=citations_converter)
    data = attr.ib()

    def __attrs_post_init__(self):
        for k, v in COL_MAP.items():
            if k in self.data:
                self.data[v] = self.data.pop(k)

        for k in self.data:
            v, refs = value_and_refs(self.data[k])
            for ref in refs:
                assert ref in self.citations
                self.citations[ref].append(k)
            self.data[k] = col_type(k)(v) if v else None

    @classmethod
    def from_row(cls, row):
        row = {k.replace(' ', '_'): v for k, v in row.items()}
        return cls(
            id=row.pop('UNIQUE_ID'),
            name=row.pop('SAMPLE_NAME'),
            citations=row.pop('CITATIONS'),
            data=row,
        )

    @property
    def region(self):
        return self.data.get('LOCATION', '').split(' / ')[0]


class GEOROC(API):
    @lazyproperty
    def converters(self):
        import importlib.util

        mod = self.path('converters.py')
        if mod.exists():
            spec = importlib.util.spec_from_file_location("pygeoroc.converters", mod)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        return argparse.Namespace(COORDINATES={}, FIELDS={})  # pragma: no cover

    @property
    def csvdir(self) -> pathlib.Path:
        return self.path('csv')

    @property
    def dbpath(self) -> pathlib.Path:
        return self.path('georoc.sqlite')

    def dbquery(self, sql, params=None):
        with sqlite3.connect(str(self.dbpath)) as conn:
            with contextlib.closing(conn.cursor()) as cu:
                cu.execute(sql, params or ())
                cols = [r[0] for r in cu.description]
                res = [collections.OrderedDict(zip(cols, row)) for row in cu.fetchall()]
        return res

    @property
    def index(self):
        with update(self.path('datasets.json'), default=[], indent=4) as data:
            return [Dataset(md) for md in data]

    @index.setter
    def index(self, datasets):
        dump(datasets, self.path('datasets.json'), indent=4)

    def iter_files(self):
        for ds in self.index:
            yield from ds.files

    def iter_references(self):
        refs = {}
        for f in self.iter_files():
            for id_, ref in f.iter_references(self):
                if id_ not in refs:
                    yield id_, ref
                    refs[id_] = ref
                else:
                    assert refs[id_] == ref  # pragma: no cover

    def iter_samples(self):
        sids = set()
        for f in self.iter_files():
            for sample in f.iter_samples(self):
                if sample.id not in sids:
                    yield sample, f
                    sids.add(sample.id)
