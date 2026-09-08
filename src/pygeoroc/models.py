"""
Models for GEOROC repos objects.
"""
import io
import re
import logging
import zipfile
import itertools
import collections
from collections.abc import Generator
import dataclasses
from typing import Any, Optional, Type, TYPE_CHECKING

import requests
from clldutils.path import md5
from csvw import dsv

if TYPE_CHECKING:
    from .api import GEOROC

JsonObjectType = dict[str, Any]
ReferenceType = tuple[int, str]

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
CITATION_PATTERN = re.compile(r'\[(?P<ref>[0-9]+)]')  # An integer enclosed in square brackets.


def api_call(p: str) -> requests.Response:
    """Call GEOROC's dataverse API."""
    return requests.get(f'{API_URL}{p}', timeout=100)


def value_and_refs(v: str) -> tuple[str, set[str]]:
    """Parse a column value, possibly containing references."""
    refs = set()

    def repl(m):
        refs.add(m.group('ref'))
        return ''

    return CITATION_PATTERN.sub(repl, v).strip(), refs


@dataclasses.dataclass
class Sample:
    """A sample as described in a GEOROC data file."""
    id: str
    name: str
    citations: collections.OrderedDict
    data: dict[str, Any]

    @staticmethod
    def col_type(s: str) -> Type:
        """The datatype of the values of a particular column."""
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

    def __post_init__(self):
        v, res = value_and_refs(self.citations)
        assert not v
        self.citations = collections.OrderedDict([(k, []) for k in res])

        for k, v in COL_MAP.items():
            if k in self.data:
                self.data[v] = self.data.pop(k)

        for k in self.data:
            v, refs = value_and_refs(self.data[k])
            for ref in refs:
                assert ref in self.citations
                self.citations[ref].append(k)
            self.data[k] = self.col_type(k)(v) if v else None

    @classmethod
    def from_row(cls, row):  # pylint: disable=C0116
        row = {k.replace(' ', '_'): v for k, v in row.items()}
        return cls(
            id=row.pop('UNIQUE_ID'),
            name=row.pop('SAMPLE_NAME'),
            citations=row.pop('CITATIONS'),
            data=row,
        )

    @property
    def region(self) -> str:  # pylint: disable=C0116
        return self.data.get('LOCATION', '').split(' / ')[0]


@dataclasses.dataclass(frozen=True)
class File:
    """
    Represents one file in a dataset from dataverse.

    {
        "id": 47086,
        "persistentId": "doi:10.25625/1KRR1P/KHXKUP",
        "pidURL": "https://doi.org/10.25625/1KRR1P/KHXKUP",
        "filename": "2022-06-1KRR1P_ZIMBABWE_CRATON_ARCHEAN.csv",
        "contentType": "text/csv",
        "filesize": 412607,
        "storageIdentifier": "file://18180e3f56b-de8696e05ee5",
        "rootDataFileId": -1,
        "md5": "1f15c19d65fcd8b841329ad1f32737e9",
        "checksum": {
            "type": "MD5",
            "value": "1f15c19d65fcd8b841329ad1f32737e9"
        },
        "creationDate": "2022-06-20"
    }
    """
    md: JsonObjectType
    section: Optional[str]
    name: str
    date: str
    md5: str
    size: int
    id: str

    @classmethod
    def from_md(cls, md: JsonObjectType, section: Optional[str] = None) -> 'File':
        """Initialize a file from JSON metadata."""
        res = cls(
            md=md,
            section=section,
            name=md['filename'],
            date=md['creationDate'],
            md5=md['md5'],
            size=md['filesize'],
            id=md['persistentId'],
        )
        assert res.name == res.name.strip()
        return res

    def exists(self, repos: 'GEOROC') -> bool:
        """
        Checks whether the specified file exists with correct checksum in the repository.
        """
        p = repos.csvdir / self.name
        return p.exists() and md5(p) == self.md5

    def iter_lines(self, repos: 'GEOROC') -> Generator[str, None, None]:
        """Yield lines of the file."""
        for line in repos.csvdir.joinpath(self.name).open(encoding='cp1252'):
            if line.strip():
                yield line.strip()

    def iter_samples(self, repos: 'GEOROC', stdout=False) -> Generator['Sample', None, None]:
        """Yield samples."""
        lines = itertools.takewhile(
            lambda ln: not (ln.startswith('Abbreviations') or ln.startswith('References:')),
            self.iter_lines(repos))
        for i, row in enumerate(dsv.reader(lines, dicts=True), start=2):
            try:
                sample = Sample.from_row(row)
            except:  # pragma: no cover # noqa: E722
                print(f'{self.name}:{i}')
                raise
            repos.fix(sample, self, stdout=stdout)
            yield sample

    def iter_references(self, repos: 'GEOROC') -> Generator[ReferenceType, None, None]:
        """
        GEOROC's CSV files come with a "References" section, i.e. a list of numbered references
        appended to the CSV content, looking as follows:

            References:

            "[2079] CASTILLO P. R., FLOYD P. A., FRANCE-LANORD C.:    ISOTOPE GEOCHEMISTRY ..."

        """
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
    """Metadata for one of GEOROC's precompiled datasets."""
    def __init__(self, md: JsonObjectType):
        self.md: JsonObjectType = md
        self.doi: str = f"{self.md['protocol']}:{self.md['authority']}/{self.md['identifier']}"
        self._citation_data = {
            f['typeName']: f['value'] for f in
            self.md['latestVersion']['metadataBlocks']['citation']['fields']}
        self.name: str = self._citation_data['title']

    @classmethod
    def from_doi(cls, doi: str) -> 'Dataset':
        """Initialize a dataset from a DOI."""
        return cls(api_call(f'datasets/:persistentId/?persistentId={doi}').json()['data'])

    @property
    def citation(self) -> str:
        """A citation for the dataset."""
        title = self._citation_data['title']
        res = ' and '.join([v['authorName']['value'] for v in self._citation_data['author']])
        res += f", {self._citation_data['dateOfDeposit'].split('-')[0]}, "
        res += f'"{title}", '
        res += f"{self.md['persistentUrl']}, "
        res += f"{self.md['publisher']}, "
        res += f"V{self.md['latestVersion']['versionNumber']}"
        return res

    @property
    def files(self) -> list[File]:
        """List of file specifications."""
        return [
            File.from_md(r['dataFile'], section=self.name)
            for r in self.md['latestVersion']['files']]

    def download_files(self, repos: 'GEOROC', log: Optional[logging.Logger] = None):
        """Download the files for the dataset if necessary."""
        def info(msg, *args):
            if log:
                log.info(msg, *args)

        # Check, whether we have to download any files:
        missing = {f.name for f in self.files if not f.exists(repos)}
        print(missing)
        if missing:
            info('Downloading files for dataset "%s" ...', self.name)
            r = api_call(f'access/dataset/:persistentId/?persistentId={self.doi}')
            repos.csvdir.mkdir(exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for name in z.namelist():
                    assert name == name.strip()
                    if name in missing:
                        info('Updating file %s', name)
                        repos.csvdir.joinpath(name).write_bytes(z.read(name))
            info('... done')
        else:
            info('Skipping download for dataset "%s". All files up-to-date.', self.name)
