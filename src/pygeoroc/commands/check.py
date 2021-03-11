"""

"""
from pygeoroc.api import EXCLUDE


def register(parser):
    parser.add_argument('--pattern', default=None, help='substring in filename')


def run(args):
    for f in args.repos.index:
        if f.section not in EXCLUDE:
            if (args.pattern is None) or args.pattern in f.name:
                for _ in f.iter_samples(args.repos, stdout=True):
                    pass
