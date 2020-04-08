"""
Load GEOROC data into a SQLite database
"""
import gzip
import shutil

from clldutils.clilib import PathType

from pygeoroc.db import Database


def register(parser):
    parser.add_argument('-f', '--force', default=False, action='store_true')
    parser.add_argument('--archive', type=PathType(type='dir'))


def run(args):
    if args.repos.dbpath.exists():
        if args.force:
            args.repos.dbpath.unlink()
        else:
            print('DB exists at {}. Use --force to recreate.'.format(args.repos.dbpath))
            return
    db = Database(args.repos.dbpath)
    db.create(args.repos)
    if args.archive:
        with args.repos.dbpath.open('rb') as f_in:
            with gzip.open(
                    str(args.archive / '{}.gz'.format(args.repos.dbpath.name)), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    args.log.info(args.repos.dbpath)
