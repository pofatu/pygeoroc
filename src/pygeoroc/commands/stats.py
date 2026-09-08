"""
Summary stats for the data loaded into the SQLite db.
"""
import argparse

from clldutils.clilib import Table, add_format


def register(parser: argparse.ArgumentParser):  # pylint: disable=C0116
    add_format(parser, 'pipe')
    parser.add_argument('--dbpath', default=None, help=argparse.SUPPRESS)


def run(args: argparse.Namespace):  # pylint: disable=C0116
    print("""# Database statistics
""")
    with Table(args, 'table', '# rows') as t:
        for table in ['file', 'reference', 'sample', 'citation']:
            t.append([table, args.repos.dbquery(f'SELECT count(*) AS c FROM {table}')[0]['c']])
