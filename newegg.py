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
from collections import OrderedDict

baseUrl = 'http://www.newegg.com/Product/'
searchPath = 'ProductList.aspx?Submit=ENE&IsNodeId=1&'
productPath = 'Product.aspx?'

categoryUrls = {
    'systems': 'http://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=100006550&isNodeId=1&Description=computer', # Home > Computer Systems > Search; VERY UNRELIABLE, as many miscellaneous product (including accessories) are exposed under this category listing
    'processors': 'http://www.newegg.com/Processors-Desktops/SubCategory/ID-343', # Home > Components > CPUs / Processors > Processors - Desktop
    'memory': 'http://www.newegg.com/Desktop-Memory/SubCategory/ID-147', # Home > Components > Memory > Desktop Memory
    'motherboard': 'http://www.newegg.com/Motherboards/Category/ID-20', # Home > Computer Systems > Monitors > LCD/LED Monitors
    'graphics': 'http://www.newegg.com/Desktop-Graphics-Cards/SubCategory/ID-48', # Home > Components > Video Cards & Video Devices > Desktop Graphics Card
    'power': 'http://www.newegg.com/Power-Supplies/SubCategory/ID-58', # Home > Components > Power Supplies > Power Supplies
    'case': 'http://www.newegg.com/Computer-Cases/SubCategory/ID-7', # Home > Components > Computer Cases > Computer Cases
    'storage': 'http://www.newegg.com/Desktop-Internal-Hard-Drives/SubCategory/ID-14' # Home > Components > Hard Drives > Desktop Internal Hard Drives
}

searchNodes = {
    'systems': 100006550,
    'processors': 10000767,
    'memory': 100007611,
    'motherboard': [100007625,100007627],
    'graphics': 100007709,
    'power': 100007657,
    'case': 100007583,
    'storage': 100167523
}

entriesPerScrape = 90 # or 15 or 30 or 60
sortBy = 'RATING' # or PRICE or REVIEWS or BESTSELLING

def _isItem(tag):
    return tag.name == 'div' and 'class' in tag.attrs and 'itemCell' in tag.attrs['class']
    
def _isTitle(tag):
    return tag.name == 'a' and 'title' in tag.attrs and tag.attrs['title'].lower() == 'view details'

def _getList(term, category='systems'):
    term = term.replace(' ', '+')
    url = baseUrl + searchPath + ('Order=%s&PageSize=%u&' % (sortBy, entriesPerScrape)) + ('N=%u&SrchInDesc=%s' % (searchNodes[category], term))
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    items = soup.find_all(_isItem)
    results = OrderedDict()
    for ndx, item in enumerate(items):
        a = item.find(_isTitle)
        m = re.search('Item=([^&]+)', a['href'])
        if m is not None:
            # We skip cases in which list entries are not specific items
            k = m.groups()[0].encode('ascii', 'ignore')
            v = a.find('span').text.encode('ascii', 'ignore')
            results[k] = v
    return results
    
def _getTitle(soup):
    title = soup.find(id='grpDescrip_h')
    return title.text
    
def _getPrice(soup):
    seller = soup.find('div', id='frmSeller')
    m = re.search('"price":(.+?),', seller.text)
    return float(m.groups()[0])
    
def _getSpecs(soup):
    specs = soup.find(id='Specs')
    dli = specs.find_all('dl')
    result = {}
    for dl in dli:
        k = dl.find('dt').text.strip()
        v = dl.find('dd').text.strip()
        result[k] = v
    return result

def getCategories():
    return searchNodes.keys()
        
def resolve(term, category='systems'):
    itemList = _getList(term, category)
    itemCode = itemList.keys()[0]
    return baseUrl + productPath + 'Item=%s' % itemCode
    
def query(url):
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    specs = _getSpecs(soup)
    specs['title'] = _getTitle(soup)
    specs['price'] = _getPrice(soup)
    return specs
