"""Defines behaviors for scraping and modeling aerospace systems data from the
   site astronautix.com
"""

import requests
import bs4
import google
import copy
import sys
import pprint
import re
import urlparse
from os import path

url = ''

def resolveUrl(href, baseUrl=None):
    if baseUrl is None:
        baseUrl = url
    absUrl = ''
    pr = urlparse.urlparse(baseUrl)
    pth,_ = path.split(pr.path)
    parts = pth.split('/')
    if href.startswith('..'):
        pre = href.split('/')
        n = 0
        while n < len(pre) and pre[n] == '..':
            n += 1
        parts = parts[0:-n]
        parts = [p for p in parts if len(p) > 0]
        href = '/'.join(pre[n:])
        absUrl = pr.netloc + '/' + '/'.join(parts) + '/' + href
    elif href.startswith('.'):
        href = href[1:]
        absUrl = pr.netloc + '/' + '/'.join(parts) + '/' + href
    elif re.match('https?://', href):
        return href
    else:
        absUrl = pr.netloc + '/' + '/'.join(parts) + '/' + href
    return pr.scheme + '//' + absUrl.replace('//', '/')
    
def getTitle(article):
    # BS4 will parse the title string into a br tag
    header = article.find('h1')
    return header.find('br').text.strip()
    
def getSummary(article):
    # The article summary is the 
    hr = article.find('hr')
    ns = [ch for ch in hr.children if type(ch) is bs4.element.NavigableString]
    return ns[-1].strip().encode('ascii', 'ignore')

def getContent(article):
    paragraphs = []
    hr = article.find('hr')
    p = hr.find('p')
    while p is not None:
        txt = next(p.children).strip()
        if len(txt) > 0:
            paragraphs.append(txt.encode('ascii', 'ignore'))
        p = p.find('p')
    return '\n\n'.join(paragraphs)

def getSpecs(article):
    s = []
    p = article.find('p')
    pp = None
    specs = {}
    k = ''
    v = ''
    while p is not None:
        i = p.find_all('i', recursive=False)
        if i is not None and len(i) > 0:
            for ch in p.children:
                if ch.name == 'i':
                    k = ch.text
                else:
                    if len(k) > 0:
                        v = ch.strip().encode('ascii', 'ignore')
                        v = re.sub('\.$', '', v)
                        specs[k] = v
                        k = ''
        pp = p
        p = p.find('p')
    p = pp.find('br')
    while p is not None:
        i = p.find_all('i', recursive=False)
        if i is not None and len(i) > 0:
            for ch in p.children:
                if ch.name == 'i':
                    k = ch.text
                else:
                    if len(k) > 0:
                        v = ch.strip().encode('ascii', 'ignore')
                        v = re.sub('\.$', '', v)
                        specs[k] = v
                        k = ''
        p = p.find('br')    
    return specs
   
def isAssoc(tag):
    return tag.name in ['hr','b','ul']
    
def getAssoc(article):
    tags = article.find_all(isAssoc)
    assocs = {}
    k = ''
    v = ''
    for ndx, tag in enumerate(tags):
        if tag.name == 'b' and tags[ndx-1].name == 'hr':
            k = tag.text.strip().encode('ascii', 'ignore')
            k = re.sub('^Associated\s*', '', k)
            k = re.sub('^Bibliography$', '', k) # To re-enable sources, replace with a non-zero-length string
            k = re.sub('^See also$', 'Topics', k)
            assocs[k] = []
        else:
            if tag.name == 'ul' and len(k) > 0:
                try:
                    name = tag.find('a').text
                    link = resolveUrl(tag.find('a').attrs['href'])
                    assocs[k].append({name:link})
                except Exception as e:
                    print('Failed to parse association value from "%s"' % str(tag))
    return assocs
                
articleModelMap = {
    'title': getTitle,
    'summary': getSummary,
    'content': getContent,
    'specifications': getSpecs,
    'associations': getAssoc
}

def pull(term):
    url = google.lucky('site:astronautix.com ' + term)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    article = soup.find('div', attrs={'id':'col1'})
    data = copy.deepcopy(articleModelMap)
    for k,v in articleModelMap.iteritems():
        data[k] = v(article)
    return data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        data = pull(sys.argv[1])
    else:
        print('Running test w/ RS-25:')
        data = pull('rs-25')
    pprint.pprint(data)
