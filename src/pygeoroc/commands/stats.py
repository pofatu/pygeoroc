"""

"""
import argparse

from clldutils.clilib import Table, add_format


def register(parser):
    add_format(parser, 'pipe')
    parser.add_argument('--dbpath', default=None, help=argparse.SUPPRESS)


def run(args):
    print("""# Database statistics
""")
    with Table(args, 'table', '# rows') as t:
        for table in ['file', 'reference', 'sample', 'citation']:
            t.append([table, args.repos.dbquery(f'SELECT count(*) AS c FROM {table}')[0]['c']])
