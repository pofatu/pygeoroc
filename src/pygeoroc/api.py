import re
import datetime
import itertools

from clldutils.apilib import API
from csvw import dsv
import attr

# We exclude files in redundant sections of the precompilations when iterating over samples:
EXCLUDE = ['Minerals', 'Rocks', 'Inclusions']
COL_MAP = {
    'ELEVATION (MAX.)': 'ELEVATION MAX',
    'ELEVATION (MIN.)': 'ELEVATION MIN',
    'LATITUDE (MAX.)': 'LATITUDE MAX',
    'LATITUDE (MIN.)': 'LATITUDE MIN',
    'LONGITUDE (MAX.)': 'LONGITUDE MAX',
    'LONGITUDE (MIN.)': 'LONGITUDE MIN',
}


def normalized(row):
    for k, v in COL_MAP.items():
        if k in row:
            row[v] = row.pop(k)
        if v in row:
            row[v] = float(row[v]) if row[v] else None
    return {k.replace(' ', '_'): v for k, v in row.items()}


def citation_converter(s):
    res = []
    for ss in s.split('['):
        ss = ss.strip()
        if ss:
            assert ss.endswith(']')
            res.append(ss[:-1].strip())
    return res


@attr.s
class Sample:
    id = attr.ib()
    name = attr.ib()
    citations = attr.ib(converter=citation_converter)
    data = attr.ib()

    @classmethod
    def from_row(cls, row):
        row = normalized(row)
        assert re.match('[0-9\[\]]+$', row['CITATIONS'])
        return cls(
            id=row.pop('UNIQUE_ID'),
            name=row.pop('SAMPLE_NAME'),
            citations=row.pop('CITATIONS'),
            data=row,
        )

    @property
    def region(self):
        return self.data.get('LOCATION', '').split(' / ')[0]


def date_converter(s):
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}$', s):
        return datetime.date(*map(int, s.split('-')))
    m, d, y = map(int, s.split('/'))
    return datetime.date(year=y, month=m, day=d)


@attr.s
class File:
    name = attr.ib()
    date = attr.ib(converter=date_converter)
    section = attr.ib(converter=lambda s: s.strip())

    @property
    def id(self):
        return self.name.split('__')[1].replace('.csv', '')

    def path(self, repos):
        return repos.path('csv', self.name)

    def size(self, repos):
        return self.path(repos).stat().st_size

    def iter_lines(self, repos):
        for line in self.path(repos).open(encoding='cp1252'):
            if line.strip():
                yield line.strip()

    def iter_samples(self, repos):
        lines = itertools.takewhile(
            lambda l: not (l.startswith('Abbreviations') or l.startswith('References:')),
            self.iter_lines(repos))
        for row in dsv.reader(lines, dicts=True):
            yield Sample.from_row(row)

    def iter_references(self, repos):
        in_refs = False
        for line in self.iter_lines(repos):
            if in_refs:
                if line.startswith('"'):
                    line = line[1:].strip()
                if line.endswith('"'):
                    line = line[:-1].strip()
                m = re.match('\[(?P<id>[0-9]+)\]\s+(?P<ref>.+)', line)
                if m:
                    yield int(m.group('id')), m.group('ref')

            if line.startswith('References:'):
                in_refs = True


class GEOROC(API):
    @property
    def dbpath(self):
        return self.path('georoc.sqlite')

    @property
    def index(self):
        fname = self.path('index.csv')
        if fname.exists():
            return [File(**d) for d in dsv.reader(fname, dicts=True)]
        if not self.path('csv').exists():
           self.path('csv').mkdir()
        return []

    @index.setter
    def index(self, items):
        with dsv.UnicodeWriter(self.path('index.csv')) as w:
            w.writerow([f.name for f in attr.fields(File)])
            for item in items:
                w.writerow(attr.astuple(item))

    def iter_references(self):
        refs = {}
        for f in self.index:
            if f.section not in EXCLUDE:
                for id_, ref in f.iter_references(self):
                    if id_ not in refs:
                        yield id_, ref
                        refs[id_] = ref
                    else:
                        assert refs[id_] == ref

    def iter_samples(self):
        sids = set()
        for f in self.index:
            if f.section not in EXCLUDE:
                for sample in f.iter_samples(self):
                    if sample.id not in sids:
                        yield sample, f
                        sids.add(sample.id)
