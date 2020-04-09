"""
List the contents of the local GEOROC repository
"""
import itertools

from clldutils.clilib import Table, add_format
from clldutils.misc import format_size

from pygeoroc.api import EXCLUDE


def register(parser):
    parser.add_argument('--sections-only', default=False, action='store_true')
    parser.add_argument('--section', default=None)
    add_format(parser, 'simple')
    parser.add_argument('--samples', default=False, action='store_true')
    parser.add_argument('--references', default=False, action='store_true')


def run(args):
    if args.sections_only:
        with Table(args, 'section', 'files', 'size') as t:
            for section, files in itertools.groupby(
                sorted(args.repos.index, key=lambda f: f.section),
                lambda f: f.section,
            ):
                files = list(files)
                t.append([
                    section,
                    len(files),
                    format_size(sum(f.size(args.repos) for f in files))])
        return

    with Table(args, 'file', 'section', 'size', 'last modified') as t:
        if args.samples:
            t.columns.append('# samples')
        if args.references:
            t.columns.append('# references')
        t.columns.append('path')
        for f in args.repos.index:
            if not args.section or (args.section == f.section):
                row = [
                    f.id,
                    f.section,
                    format_size(f.size(args.repos)),
                    f.date.isoformat()
                ]
                if args.samples:
                    if f.section in EXCLUDE:  # pragma: no cover
                        row.append(0)
                    else:
                        row.append(len(list(f.iter_samples(args.repos))))
                if args.references:
                    row.append(len(list(f.iter_references(args.repos))))
                row.append(f.path(args.repos))
                t.append(row)
