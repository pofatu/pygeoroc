"""
Functionality to load GEOROC data into an SQLite db.
"""
import re
import sqlite3
import contextlib
import collections
from typing import TYPE_CHECKING

from tqdm import tqdm
from pygeoroc.models import Sample

if TYPE_CHECKING:
    from .api import GEOROC


def create(api: 'GEOROC'):
    """Load data from repository into SQLite database."""
    cols, files = {}, []
    for f in api.iter_files():
        files.append(f)
        for sample in f.iter_samples(api):
            for key in sample.data:
                if key:
                    cols[key] = 'REAL' if Sample.col_type(key) is float else 'TEXT'
            break
    cols = collections.OrderedDict(sorted(
        cols.items(),
        key=lambda s: ('(' in s[0], bool(re.search('[0-9]', s[0])), s[0])))

    with contextlib.closing(sqlite3.connect(str(api.dbpath))) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        with contextlib.closing(conn.cursor()) as cu:
            _create_schema(cu, cols)
            _load_data(cu, cols, api, files)
        conn.commit()


def _create_schema(cu: sqlite3.Cursor, cols: dict[str, str]):
    def create_table(name, *clauses):
        cu.execute(f"CREATE TABLE {name} ({', '.join(clauses)})")

    create_table("file", "id TEXT PRIMARY KEY", "date TEXT", "section TEXT")
    create_table("reference", "id INTEGER PRIMARY KEY", "reference TEXT")
    spec = ['id TEXT PRIMARY KEY', 'file_id TEXT']
    spec.extend([f'`{k}` {v}' for k, v in cols.items()])
    spec.append('FOREIGN KEY (file_id) REFERENCES file(id)')
    create_table("sample", *spec)
    create_table(
        "citation",
        "sample_id TEXT",
        "reference_id INTEGER",
        "fields TEXT",
        "FOREIGN KEY (sample_id) REFERENCES sample(id)",
        "FOREIGN KEY (reference_id) REFERENCES reference(id)")


def _load_data(cu: sqlite3.Cursor, cols: dict[str, str], api, files):
    def insert(table, cols, rows):
        cols = [f'`{c}`' for c in cols]
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
        cu.executemany(sql, rows)

    refs, samples = set(), set()
    for f in tqdm(files):
        insert('file', ('id', 'date', 'section'), [(f.name, f.date, f.section)])
        for id_, ref in f.iter_references(api):
            if id_ not in refs:
                insert("reference", ("id", "reference"), [(id_, ref)])
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
        insert("sample", ['id', 'file_id'] + list(cols), tuples)
        insert("citation", ("sample_id", "reference_id", "fields"), citations)
