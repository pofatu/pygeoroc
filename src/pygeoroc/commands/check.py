"""

"""


def register(parser):
    parser.add_argument('--pattern', default=None, help='substring in filename')


def run(args):
    for f in args.repos.iter_files():
        if (args.pattern is None) or args.pattern in f.name:
            for _ in f.iter_samples(args.repos, stdout=True):
                pass
