"""
Check the CSV data for consistency.
"""
import argparse


def register(parser: argparse.ArgumentParser):  # pylint: disable=C0116
    parser.add_argument('--pattern', default=None, help='substring in filename')


def run(args: argparse.Namespace):  # pylint: disable=C0116
    files = {f.name: f for f in args.repos.iter_files()}
    for fname in args.repos.converters.COORDINATES:
        if fname not in files:
            args.log.warning(fname)
    for f in files.values():
        if (args.pattern is None) or args.pattern in f.name:
            for _ in f.iter_samples(args.repos, stdout=True):
                pass
