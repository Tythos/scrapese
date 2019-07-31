"""
"""

import os
import bs4
import requests

FACTBOOK_URL = "https://www.cia.gov/library/publications/the-world-factbook"

def getFlags(destPath=None):
    """Scraps country flags from the factbook into the specified icon folder.
    """
    if destPath is None:
        modPath, _ = os.path.split(os.path.abspath(__file__))
        destPath = modPath + "/flags"
        print("Defaulting flag destination to '%s'..." % destPath)
    if not os.path.isdir(destPath):
        os.mkdir(destPath)
    pathUrl = FACTBOOK_URL + "/docs"
    res = requests.get(pathUrl + "/flagsoftheworld.html")
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    flagDivs = soup.find_all("div", {"class": "flag-image"})
    print("Scraping %u nation flags..." % len(flagDivs))
    for ndx, flagDiv in enumerate(flagDivs):
        img = flagDiv.find("img")
        src = img.get_attribute_list("src")[0]
        res = requests.get(pathUrl + "/" + src)
        _, fileName = os.path.split(src)
        name, ext = os.path.splitext(fileName)
        parts = name.split("-")
        flagDest = destPath + "/%s%s" % (parts[0], ext)
        with open(flagDest, "wb") as f:
            f.write(res.content)
        print("%u. Scraped and saved flag for %s" % (ndx, parts[0]))

if __name__ == "__main__":
    getFlags()
