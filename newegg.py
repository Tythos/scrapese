"""Defines routines for scraping component database entries from newegg.com from
   one of the following categories:
    * Components > CPUs / Processors > Processors - Desktop
    * Components > Memory > Desktop Memory
    * Components > Motherboards
    * Components > Video Cards & Video Devices > Desktop Graphics Cards
    * Components > Power Supplies > Power Supplies
    * Components > Computer Cases > Computer Cases
    * Components > Hard Drives > Desktop Internal Hard Drives
    
   At this stage, only basic queries are performed for insertion into a local
   database. Eventually, we will need to explore a filtering mechanism based on
   constraints imposed by existing selections.
"""

import sys
import requests
import bs4
import re

categoryUrls = {
    'processors': 'http://www.newegg.com/Processors-Desktops/SubCategory/ID-343',
    'memory': 'http://www.newegg.com/Desktop-Memory/SubCategory/ID-147',
    'motherboard': 'http://www.newegg.com/Motherboards/Category/ID-20',
    'graphics': 'http://www.newegg.com/Desktop-Graphics-Cards/SubCategory/ID-48',
    'power': 'http://www.newegg.com/Power-Supplies/SubCategory/ID-58',
    'case': 'http://www.newegg.com/Computer-Cases/SubCategory/ID-7',
    'storage': 'http://www.newegg.com/Desktop-Internal-Hard-Drives/SubCategory/ID-14'
}

entriesPerScrape = 15
sortBy = 'RATING'

def isItem(tag):
    return tag.name == 'div' and 'class' in tag.attrs and 'itemCell' in tag.attrs['class']
    
def isTitle(tag):
    return tag.name == 'span' and 'id' in tag.attrs and re.match('lineDescriptionID\d+', tag.attrs['id'])

def main(category):
    url = categoryUrls[category] + '?Order=%s&Pagesize=%u' % (sortBy, entriesPerScrape)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    items = soup.find_all(isItem)
    for i in items:
        title = i.find_all(isTitle)[0].text
        print(title)
    
if __name__ == '__main__':
    main(sys.argv[1])
