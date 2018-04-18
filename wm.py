"""Defines routines for scraping technical data from several WikiMedia table and
   template formats--specifically, compmarison and infobox tables.
"""

import sys
import requests
import bs4
import re
import json
from dateutil import parser

def parseLatLon(text):
    """Degrees/minutes/seconds notation (including cardinal direction) parsed
       and converted to float value; returned in two-element tuple along with
       single-characater cardinal direction.
    """
    d, m, s, c = re.split('[^\w]', text)
    value = float(d) + float(m) / 60 + float(s) / 3600
    return value, c

def getLatLon(soup):
    """Scrapes latitude and longitude coordinates from geotag on WM page
    """
    lat = soup.find('span', {'class': 'latitude'})
    latval, cardin = parseLatLon(lat.text)
    if cardin.lower() == 's':
        latval = -1 * latval
    lon = soup.find('span', {'class': 'longitude'})
    lonval, cardin = parseLatLon(lon.text)
    if cardin.lower() == 'w':
        lonval = -1 * lonval
    return latval, lonval

def isInfobox(tag):
    """Filter for determining if a given table element is a WikiMedia infobox
    """
    return tag.name == 'table' and 'class' in tag.attrs and 'infobox' in tag.attrs['class']
    
def isRow(tag):
    """Filter for determining if a given element is a WikiMedia table row
    """
    return tag.name == 'tr' and len(tag.find_all(['td','th'])) == 2

def isWikiTable(tag):
    """Filter for determining if a given element is a WikiMedia table entry
    """
    return tag.name == 'table' and 'class' in tag.attrs and 'wikitable' in tag.attrs['class']
    
def isDataRow(tag):
    """Filter for determining if a given sub-table element is a non-header row
    """
    return tag.name == 'tr' and len(tag.find_all('th')) == 0
    
def filter(phrase, isSpecCharsFiltered=True):
    """Processes key and value strings for dictionary storage, including
       condensation of whitespace, removal of bracketed references, and (if not
       specified otherwise) removal of non-word/space/digit characters.
    """
    # phrase = phrase.encode('ascii', 'ignore')
    phrase = re.sub('[\-\s]+', ' ', phrase)
    phrase = re.sub('\[.+?\]', '', phrase)
    if isSpecCharsFiltered:
        phrase = re.sub('[^\w\s\d]+', '', phrase)
    return phrase
    
def getInfoBox(url):
    """Returns a dictionary corresponding to the entries in the first infobox
       (usually an article card) from the page at the given URL.
    """
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    table = soup.find_all(isInfobox)[0]
    entry = {}
    for r in table.find_all(isRow):
        k, v = [c.text for c in r.find_all(['td','th'])]
        key = filter(k).strip()
        if key in entry:
            entry[key] = entry[key] + '; ' + filter(v, False)
        else:
            entry[key] = filter(v, False)
    return entry
    
def getTables(url):
    """Returns a set of parsed tables for all tables in the given page. No
       schema is assumed; table cells are simply parsed as filtered text values.
    """
    result = []
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    tables = soup.find_all('table')
    for table in tables:
        result.append(getTable('', table))
    return result
    
def getVisibleChildren(tag):
    chi = [ch for ch in tag.children]
    for ch in tag.children:
        if hasattr(ch, 'attrs'):
            if 'style' in ch.attrs:
                if 'display:none' in ch.attrs['style']:
                    chi.remove(ch)
    return chi

def attemptDate(value):
    try:
        value = parser.parse(value)
        if value.hour is 0 and value.minute is 0 and value.second is 0:
            value = value.date()
    except:
        pass
    return value
    
def getTable(url='', table=None):
    """Fetches, parses, and returns the desired table (defaults to the first) on
       the given WikiMedia-served page. Technically, would work with any .HTML
       page with a table, in fact. The main difference between getTable() and
       getCompList() is the lack of assumption regarding table schema--no
       headers are required and data is simply returned as a list of lists.
    """
    if type(table) is not bs4.element.Tag:
        res = requests.get(url)
        soup = bs4.BeautifulSoup(res.content, 'html.parser')
        tables = soup.find_all('table')
        if type(table) in [type(0), type(0.)]:
            table = tables[int(table)]
        else:
            table = tables[0]
    entries = []
    for r in table.find_all('tr'):
        entry = []
        for ndx, cell in enumerate(r.find_all(['th','td'])):
            chi = getVisibleChildren(cell)
            values = []
            for ch in chi:
                if type(ch) is bs4.element.NavigableString:
                    values.append(ch)
                else:
                    values.append(ch.text)
            if len(values) == 0:
                value = cell.text.strip()
            else:
                value = ' '.join(values).strip()
            value = value.replace(u'\xa0', ' ')
            value = attemptDate(value)
            if type(value) in [type(0),type(0.)]:
                value = re.sub('\[.+?\]', '', value)
            entry.append(value)
        entries.append(entry)
    return entries
    
def getCompList(url, table=None):
    """Returns a list of dictionaries corresponding to the table entries (header
       row assumed) from the first WikiMedia-style table on the page at the 
       given URL. This is typically used for 'Comparison of' or 'List of' pages.
    """
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    tables = soup.find_all(isWikiTable)
    if type(table) in [type(''),type(u'')]:
        ths = [filter(t.find('th').text).lower() for t in tables]
        table = tables[ths.index(table.lower())]
    elif type(table) in [type(0),type(0.)]:
        table = tables[int(table)]
    else:
        table = tables[0]
    headers = [filter(h.text) for h in table.find_all('th')]
    entries = []
    for r in table.find_all(isDataRow):
        entry = {}
        for ndx, cell in enumerate(r.find_all('td')):
            value = ' '.join([ch for ch in cell.children if type(ch) is bs4.element.NavigableString])
            if len(value) == 0:
                value = cell.text
            entry[headers[ndx]] = filter(value, False)
        entries.append(entry)
    return entries
    
def getUrl(articleName, fqdn='https://en.wikipedia.org/', apiPath='w/api.php', exceptNull=False):
    """Uses the WikiMedia API to determine the ID of a page with the given
       title, which is then used to construct a stable URL for the corresponding
       page.
    """
    queryString = '?action=query&prop=info&format=json&titles=' + articleName.replace(' ', '%20')
    res = requests.get(fqdn + apiPath + queryString)
    data = json.loads(res.content)
    pages = data['query']['pages']
    keys = list(pages.keys())
    id = int(keys[0])
    if id < 0 and exceptNull:
        raise Exception('Null page returned for article name "%s"' % articleName)
    return '%s?curid=%u' % (fqdn, id)

def main(topic):
    """By default, scrapes the infobox from the given topic page into a
       dictionary that is then returned.
    """
    url = getUrl(topic)
    ib = getInfoBox(url)
    return ib

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception('Command-line invocation requires a topic argument')
    IB = main(sys.argv[1])
    print(json.dumps(IB, indent=4))
