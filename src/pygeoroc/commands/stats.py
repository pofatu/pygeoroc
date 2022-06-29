"""

"""
import sqlite3
import argparse

from clldutils.clilib import Table, add_format


def register(parser):
    add_format(parser, 'pipes')
    parser.add_argument('--dbpath', default=None, help=argparse.SUPPRESS)


def run(args):
    conn = sqlite3.connect(args.dbpath or args.repos.dbpath)
    cu = conn.cursor()
    print("""# Database statistics
""")
    with Table(args, 'table', '# rows') as t:
        for table in ['file', 'reference', 'sample', 'citation']:
            cu.execute('SELECT count(*) FROM {}'.format(table))
            t.append([table, cu.fetchone()[0]])
