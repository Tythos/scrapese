"""Wraps requests to celestrak.com to facilitate catalog and TLE queries.
"""

import re
import bs4
import csv
import google
import requests
from sgp4 import earth_gravity, io
from scrapese import data

ctUrl = 'http://celestrak.com'
catUrl = ctUrl + '/pub/satcat.txt'
tleUrl = ctUrl + '/cgi-bin/TLE.pl?CATNR=%05u'
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
        sscid = int(sscid)
    return tleUrl % sscid

def convertSatcat(scPath=catPath):
    """Parses a satcat.txt file into a satcat.csv file, written to the same
       location, using a known schema. By default, this will be dbPath.
    """
    with open(scPath, 'r') as f:
        lines = f.readlines()
    entries = []
    for line in lines:
        objType = \
            "PAY" if line[20] == "*" else \
            "R/B" if line[23:47].strip().endswith("R/B") else \
            "DEB" if line[23:47].strip().endswith("DEB") else "UNK"
        dataStatus = \
            "NCE" if line[129:132].strip() == "NCE" else \
            "NIE" if line[129:132].strip() == "NIE" else \
            "NEA" if line[129:132].strip() == "NEA" else ""
        orbCenter = \
            "AS" if line[129:132].strip().startswith("AS") else \
            "EA" if line[129:132].strip().startswith("EA") else \
            "EL" if line[129:132].strip().startswith("EL") else \
            "EM" if line[129:132].strip().startswith("EM") else \
            "JU" if line[129:132].strip().startswith("JU") else \
            "MA" if line[129:132].strip().startswith("MA") else \
            "ME" if line[129:132].strip().startswith("ME") else \
            "MO" if line[129:132].strip().startswith("MO") else \
            "NE" if line[129:132].strip().startswith("NE") else \
            "PL" if line[129:132].strip().startswith("PL") else \
            "SA" if line[129:132].strip().startswith("SA") else \
            "SS" if line[129:132].strip().startswith("SS") else \
            "SU" if line[129:132].strip().startswith("SU") else \
            "UR" if line[129:132].strip().startswith("UR") else \
            "VE" if line[129:132].strip().startswith("VE") else "EA"
        orbType = \
            "ORB" if line[131] == "0" else \
            "LAN" if line[131] == "1" else \
            "IMP" if line[131] == "2" else \
            "R/T" if line[131] == "3" else \
            "DOC" if line[129:132].strip() == "DOC" else \
            "IMP" if line[21] == "D" else "ORB" 
        entries.append({
            "OBJECT_NAME": line[23:47].strip(),
            "OBJECT_ID": line[0:11].strip(),
            "NORAD_CAT_ID": line[13:18].strip(),
            "OBJECT_TYPE": objType,
            "OPS_STATUS_CODE": line[21].strip(),
            "OWNER": line[49:54].strip(),
            "LAUNCH_DATE": line[56:66].strip(),
            "LAUNCH_SITE": line[68:73].strip(),
            "DECAY_DATE": line[75:85].strip(),
            "PERIOD": line[87:94].strip(),
            "INCLINATION": line[96:101].strip(),
            "APOGEE": line[103:109].strip(),
            "PERIGEE": line[111:117].strip(),
            "RCS": line[119:127].strip(),
            "DATA_STATUS_CODE": dataStatus,
            "ORBIT_CENTER": orbCenter,
            "ORBIT_TYPE": orbType
        })
    csvPath = re.sub(r"\.txt", ".csv", scPath)
    with open(csvPath, 'w') as f:
        dw = csv.DictWriter(f, fieldnames=entries[0].keys(), lineterminator="\n")
        dw.writeheader()
        dw.writerows(entries)

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
