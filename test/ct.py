"""Contains unit tests for evaluating the celetrack scraping module
"""

import unittest
from scrapese import celestrak as ct

class TestShijan(unittest.TestCase):
    def test_resolve(self):
        url = ct.resolve('SHIJIAN')
        
    def test_query(self):
        url = ct.resolve('SHIJIAN')
        tle = ct.query(url)

if __name__ == '__main__':
    unittest.main()
