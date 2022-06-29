import re
import sqlite3
import contextlib
import collections

from tqdm import tqdm
from pygeoroc.api import col_type


class Database:
    def __init__(self, fname):
        self.fname = fname

    def create(self, api):
        cols, files = {}, []
        for f in api.iter_files():
            files.append(f)
            for sample in f.iter_samples(api):
                for key in sample.data:
                    if key:
                        cols[key] = 'REAL' if col_type(key) is float else 'TEXT'
                break
        cols = collections.OrderedDict(sorted(
            cols.items(),
            key=lambda s: ('(' in s[0], bool(re.search('[0-9]', s[0])), s[0])))

        with sqlite3.connect(str(self.fname)) as conn:
            conn.execute('PRAGMA foreign_keys = ON;')
            with contextlib.closing(conn.cursor()) as cu:
                self._create_schema(cu, cols)
                self._load_data(cu, cols, api, files)

    def _create_schema(self, cu, cols):
        cu.execute("CREATE TABLE file (id TEXT PRIMARY KEY, date TEXT, section TEXT);")
        cu.execute("CREATE TABLE reference (id INTEGER PRIMARY KEY, reference TEXT);")
        colspec = ['`{}` {}'.format(k, v) for k, v in cols.items()]
        cu.execute("""
CREATE TABLE sample (
    id TEXT PRIMARY KEY,
    file_id TEXT,
    {},
    FOREIGN KEY (file_id) REFERENCES file(id)
);
""".format(',\n'.join(colspec)))
        cu.execute("""
CREATE TABLE citation (
    sample_id TEXT,
    reference_id INTEGER,
    fields TEXT,
    FOREIGN KEY (sample_id) REFERENCES sample(id),
    FOREIGN KEY (reference_id) REFERENCES reference(id)
);
""")

    def _load_data(self, cu, cols, api, files):
        refs, samples = set(), set()
        for f in tqdm(files):
            cu.execute(
                "INSERT INTO file (id, date, section) VALUES (?,?,?)",
                (f.name, f.date, f.section))
            for id_, ref in f.iter_references(api):
                if id_ not in refs:
                    cu.execute(
                        "INSERT INTO reference (id, reference) VALUES (?,?)",
                        (id_, ref))
                    refs.add(id_)
            tuples, citations = [], []
            for sample in f.iter_samples(api):
                if sample.id not in samples:
                    samples.add(sample.id)
                    tuples.append(
                        tuple([sample.id, f.name] + [sample.data.get(c) for c in cols]))
                    citations.extend(
                        [(sample.id, cit, ' '.join(fields))
                         for cit, fields in sample.citations.items()])
            sql = "INSERT INTO sample ({}) VALUES ({})".format(
                ', '.join(['id', 'file_id'] + ['`{}`'.format(c) for c in cols]),
                ', '.join(['?' for _ in range(len(cols) + 2)]))
            cu.executemany(sql, tuples)
            cu.executemany(
                "INSERT INTO citation (sample_id, reference_id, fields) VALUES (?, ?, ?)",
                citations)
