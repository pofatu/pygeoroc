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
    parser.add_argument('--section', default=None)


def run(args):
    index = collections.OrderedDict([(f.name, f) for f in args.repos.index])
    html = bs(requests.get(INDEX).content, 'html.parser')
    header = None
    for tr in html.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 1 and tds[0].attrs.get('colspan') == '3':
            header = tds[0].get_text().strip()
        elif len(tds) == 3 and tds[0].find('a', href=True):
            if not args.section or (args.section == header):
                a = tds[0].find('a', href=True)
                if a and a['href'].endswith('.csv') and a['href'].startswith(PATH_PREFIX):
                    f = File(
                        name=a['href'].replace(PATH_PREFIX, '').replace('/', '__'),
                        section=header,
                        date=tds[2].string,
                    )
                    if (f.name not in index) or index[f.name].date < f.date:
                        args.log.info('Retrieving {}'.format(a['href']))
                        urlretrieve(BASE_URL + a['href'], str(args.repos.path('csv', f.name)))
                        index[f.name] = f

    args.repos.index = list(index.values())
