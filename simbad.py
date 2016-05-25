"""Interface to the SIMBAD star catalog database
"""

import bs4
import requests

def _getUrl(url):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, 'html.parser')
    tables = soup.find_all('table')
    for ndx, table in enumerate(tables):
        b = table.find_all('b')
        if len(b) == 1 and b[0].text.strip().startswith('Identifiers'):
            idNdx = ndx + 1
    tti = tables[idNdx].find_all('tt')
    ids = {}
    for tt in tti:
        a = tt.find('a')
        k = a.text.strip()
        v = a.next_sibling.string.strip()
        ids[k] = v
    return ids
    
def getSao(id):
    url = 'http://simbad.u-strasbg.fr/simbad/sim-id?Ident=SAO+' + str(id)
    return _getUrl(url)
    
def getOther(field, value):
    url = 'http://simbad.u-strasbg.fr/simbad/sim-id?Ident=%s+%u' % (field, value)
    return _getUrl(url)
