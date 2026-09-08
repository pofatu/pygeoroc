"""
Load GEOROC data into a SQLite database
"""
import gzip
import shutil
import subprocess

from clldutils.clilib import PathType

from pygeoroc.db import create


def register(parser):
    parser.add_argument('-f', '--force', default=False, action='store_true')
    parser.add_argument('--dump-schema', default=False, action='store_true')
    parser.add_argument('--archive', type=PathType(type='dir'))


def run(args):
    if args.repos.dbpath.exists():
        if args.force:
            args.repos.dbpath.unlink()
        else:
            print(f'DB exists at {args.repos.dbpath}. Use --force to recreate.')
            return
    create(args.repos)
    if args.dump_schema:
        print(subprocess.check_output(['sqlite3', str(args.repos.dbpath), '.schema']))
    if args.archive:
        with args.repos.dbpath.open('rb') as f_in:
            with gzip.open(
                    str(args.archive / f'{args.repos.dbpath.name}.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    args.log.info(args.repos.dbpath)
