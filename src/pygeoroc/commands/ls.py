"""
List the contents of the local GEOROC repository
"""
import argparse

from clldutils.clilib import Table, add_format
from clldutils.misc import format_size


def register(parser: argparse.ArgumentParser):  # pylint: disable=C0116
    add_format(parser, 'simple')
    parser.add_argument('--index', default=False, action='store_true')
    parser.add_argument('--citations', default=False, action='store_true')
    parser.add_argument('--datasets-only', default=False, action='store_true')
    parser.add_argument('--dataset', default=None)
    parser.add_argument('--samples', default=False, action='store_true')
    parser.add_argument('--references', default=False, action='store_true')


def run(args: argparse.Namespace):  # pylint: disable=C0116
    if args.citations:  # pragma: no cover
        for dataset in args.repos.index:
            print(f'> {dataset.citation}' + '\n')
        return

    if args.datasets_only:
        with Table(args, 'dataset', 'files', 'size') as t:
            totalfiles, totalsize = 0, 0
            for dataset in args.repos.index:
                totalfiles += len(dataset.files)
                totalsize += sum(f.size for f in dataset.files)
                t.append([
                    dataset.name,
                    len(dataset.files),
                    format_size(sum(f.size for f in dataset.files))])
            t.append(
                [f'total: {len(args.repos.index)} datasets', totalfiles, format_size(totalsize)])
        return

    if args.index:  # pragma: no cover
        args.format = 'pipe'
        print("""# Content

[georoc.sqlite.gz](georoc.sqlite.gz) contains data from
[GEOROC's precompiled datasets](https://data.goettingen-research-online.de/dataverse/digis)
as listed below.
""")

    with Table(args, 'file', 'dataset', 'size', 'last modified') as t:
        if args.samples:
            t.columns.append('# samples')
        if args.references:
            t.columns.append('# references')
        t.columns.append('path')
        for ds in args.repos.index:
            if args.dataset and (args.dataset not in ds.name):
                continue  # pragma: no cover
            for f in ds.files:
                row = [f"[{f.id}]({f.md['pidURL']})", ds.name, format_size(f.size), f.date]
                if args.samples:
                    row.append(len(list(f.iter_samples(args.repos, stdout=None))))
                if args.references:
                    row.append(len(list(f.iter_references(args.repos))))
                row.append(f.name)
                t.append(row)
