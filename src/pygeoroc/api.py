"""
Models for repository objects.
"""
import pathlib
import sqlite3
import argparse
import functools
import contextlib
import collections
from collections.abc import Generator, Sequence
from typing import Any, Optional

from clldutils.apilib import API
from clldutils.jsonlib import update, dump

from .models import Dataset, File, Sample, ReferenceType, JsonObjectType
from .errata import Converters, fix


class GEOROC(API):
    """
    Programmatic access to GEOROC data in a repository.
    """
    @functools.cached_property
    def converters(self) -> Converters:
        """Load repository-specific converters."""
        import importlib.util  # pylint: disable=C0415

        mod = self.path('converters.py')
        if mod.exists():
            spec = importlib.util.spec_from_file_location("pygeoroc.converters", mod)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        return argparse.Namespace(COORDINATES={}, FIELDS={})  # pragma: no cover

    def fix(self, sample, f, stdout=False):
        fix(sample, f, self, stdout=stdout)

    @property
    def csvdir(self) -> pathlib.Path:  # pylint: disable=C0116
        return self.path('csv')

    @property
    def dbpath(self) -> pathlib.Path:  # pylint: disable=C0116
        return self.path('georoc.sqlite')

    def dbquery(
            self,
            sql: str,
            params: Optional[Sequence[Any]] = None,
    ) -> list[collections.OrderedDict[str, Any]]:
        """Run an SQL query on the georoc sqlite db and return the result rows as dicts."""
        with contextlib.closing(sqlite3.connect(str(self.dbpath))) as conn:
            with contextlib.closing(conn.cursor()) as cu:
                cu.execute(sql, params or ())
                cols = [r[0] for r in cu.description]
                res = [collections.OrderedDict(zip(cols, row)) for row in cu.fetchall()]
            conn.rollback()
        return res

    @property
    def index(self) -> list[Dataset]:
        """The list of all datasets listed in the metadata file."""
        with update(self.path('datasets.json'), default=[], indent=4) as data:
            return [Dataset(md) for md in data]

    @index.setter
    def index(self, datasets: JsonObjectType):
        """Write the datasets metadata to a file in the repos."""
        dump(datasets, self.path('datasets.json'), indent=4)

    def iter_files(self) -> Generator[File, None, None]:
        """Yield all files in the repos."""
        for ds in self.index:
            yield from ds.files

    def iter_references(self) -> Generator[ReferenceType, None, None]:
        """Yield all references from the repos."""
        refs = {}
        for f in self.iter_files():
            for id_, ref in f.iter_references(self):
                if id_ not in refs:
                    yield id_, ref
                    refs[id_] = ref
                else:
                    assert refs[id_] == ref  # pragma: no cover

    def iter_samples(self) -> Generator[tuple[Sample, File], None, None]:
        """Yield all samples in the repos."""
        sids = set()
        for f in self.iter_files():
            for sample in f.iter_samples(self):
                if sample.id not in sids:
                    yield sample, f
                    sids.add(sample.id)
