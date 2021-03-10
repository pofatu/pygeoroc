"""
Download precompiled files from GEOROC
"""
import collections

from bs4 import BeautifulSoup as bs
import requests

from urllib.request import urlretrieve

from pygeoroc.api import File


PATH_PREFIX = '/georoc/Csv_Downloads/'
BASE_URL = "http://georoc.mpch-mainz.gwdg.de"
INDEX = BASE_URL + "/georoc/CompFiles.aspx"


def register(parser):
    parser.add_argument(
        '--autoremove',
        help="Remove CSV files which are no longer listed on GEOROC's download page",
        action='store_true',
        default=False)
    parser.add_argument('--section', default=None)


def run(args):
    index = collections.OrderedDict([(f.name, f) for f in args.repos.index])
    html = bs(requests.get(INDEX).content, 'html.parser')
    header, filenames, new = None, set(), False
    for tr in html.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 1 and tds[0].attrs.get('colspan') == '3':
            header = tds[0].get_text().strip()
        elif len(tds) == 3 and tds[0].find('a', href=True):
            a = tds[0].find('a', href=True)
            if a and a['href'].endswith('.csv') and a['href'].startswith(PATH_PREFIX):
                f = File(
                    name=a['href'].replace(PATH_PREFIX, '').replace('/', '__'),
                    section=header,
                    date=tds[2].string,
                )
                filenames.add(f.name)
                if not args.section or (args.section == header):
                    if (f.name not in index) or index[f.name].date < f.date:
                        args.log.info('Retrieving {}'.format(a['href']))
                        urlretrieve(BASE_URL + a['href'], str(args.repos.path('csv', f.name)))
                        index[f.name] = f
                        new = True

    if not new:
        args.log.info('All CSV files in the repos are up-to-date')

    obsolete = [p for p in args.repos.path('csv').iterdir() if p.name not in filenames]
    if obsolete:
        if args.autoremove:
            for p in obsolete:
                args.log.info('removing obsolete file {}'.format(p))
                p.unlink()
        else:
            args.log.info('{} obsolete CSV files in the repos. Pass --autoremove to remove!'.format(
                len(obsolete)))

    args.repos.index = [f for fname, f in index.items() if fname in filenames]
