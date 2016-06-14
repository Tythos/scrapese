"""Wraps requests to celestrak.com to facilitate catalog and TLE queries.
"""

import bs4
import google
import requests
from sgp4 import earth_gravity, io
from scrapese import data

ctUrl = 'http://celestrak.com'
catUrl = ctUrl + '/pub/satcat.txt'
tleUrl = ctUrl + '/cgi-bin/TLE.pl'
catPath = data.get_path('satcat.txt')
dbPath = data.get_path('satcat.csv')

def _updateSatCat():
    """Pulls a new copy of the satellite catalog.
    """
    response = requests.get(catUrl)
    with open(catPath, 'wb') as f:
        f.write(response.content)
    
def _readSatCatLine(line):
    """Returns the name, international designator (id), nad NORAD catalog number
       (catNum) from a line in the satellite catalog.
    """
    name = line[23:47].strip()
    id = line[0:11].strip()
    catNum = line[13:18].strip()
    return name, id, catNum
    
def resolveTle(sscid):
    """For a given SSCID (integer value), returns the URL from which the TLE can
       be requests from CelesTrak.
    """
    if type(sscid) in [type(''), type(u'')]:
        url = tleUrl + '?CATNR=' + sscid
    else:
        url = tleUrl + ('?CATNR=%05u' % sscid)
    return url
    
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
    return resolveTle(sscid)
    
def query(url):
    """Returns the TLE stored at the given URL. Will technically contain three
       lines, not two, as the first line is the full name of the object.
    """
    response = requests.get(url)
    bs = bs4.BeautifulSoup(response.content, 'html.parser')
    pre = bs.find('pre')
    return pre.string.strip().splitlines()
