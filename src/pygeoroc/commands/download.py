"""
Download precompiled files from GEOROC
"""
from pygeoroc import DATASETS
from pygeoroc.api import Dataset


def run(args):
    datasets = []
    for doi, name in sorted(DATASETS.items(), key=lambda i: i[1]):
        ds = Dataset.from_doi(doi)
        datasets.append(ds.md)
        ds.download_files(args.repos, log=args.log)
    args.repos.index = datasets
