"""
Download precompiled files from GEOROC
"""
import argparse

from pygeoroc import DATASETS
from pygeoroc.api import Dataset


def run(args: argparse.Namespace):  # pylint: disable=C0116
    datasets = []
    for doi, _ in sorted(DATASETS.items(), key=lambda i: i[1]):
        ds = Dataset.from_doi(doi)
        datasets.append(ds.md)
        ds.download_files(args.repos, log=args.log)
    args.repos.index = datasets
