"""Wraps requests to celestrak.com to facilitate catalog and TLE queries.
"""

import bs4
import google
import requests
from scrapese import data

catUrl = 'https://celestrak.com/pub/satcat.txt'
catPath = data.get_path('satcat.txt')

def _readSatCatLine(line):
    """Returns the name, international designator (id), nad NORAD catalog number
       (catNum) from a line in the satellite catalog.
    """
    name = line[23:47].strip()
    id = line[0:11].strip()
    catNum = line[13:18].strip()
    return name, id, catNum
    
def resolve(term):
    """Uses the satellite catalog page (preferably cached) to return a URL to
       the TLE resource for the given satellite, which can be resolved by name,
       international designator, or NORAD catalog number. Until caching is
       implemented, we use a locally-stored version.
    """
    with open(catPath, 'r') as f:
        txt = f.read()
    lines = txt.splitlines()
    sscid = ''
    for line in lines:
        if len(sscid) is 0:
            name, id, catNum = _readSatCatLine(line)
            if term.lower() in name.lower():
                sscid = catNum
            elif term.lower() == id.lower():
                sscid = catNum
            elif term.lower() == catNum.lower():
                sscid = catNum
    if len(sscid) is 0:
        raise Exception('Unable to resolve resource for term "%s"' % term)
    return 'http://celestrak.com/cgi-bin/TLE.pl?CATNR=' + sscid

def query(url):
    """Returns the TLE stored at the given URL. Will technically contain three
       lines, not two, as the first line is the full name of the object.
    """
    response = requests.get(url)
    bs = bs4.BeautifulSoup(response.content, 'lxml')
    pre = bs.find('pre')
    return pre.string.strip().splitlines()