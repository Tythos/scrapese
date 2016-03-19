"""Test cases for Astronautix scraping
"""

import unittest
from scrapese import astronautix

class Engine(unittest.TestCase):
    def test_resolve(self):
        url = astronautix.resolve('RS-25')
    
    def test_query(self):
        url = astronautix.resolve('RS-25')
        model = astronautix.query(url)
        areaRatio = astronautix.getValue(model, 'Area Ratio')
        expected = 77.5
        self.assertTrue(abs(expected - areaRatio) / expected < 1e-3)
        
class Craft(unittest.TestCase):
    def test_resolve(self):
        url = astronautix.resolve('X-37b')
    
    def test_query(self):
        url = astronautix.resolve('X-37b')
        model = astronautix.query(url)
        span = astronautix.getValue(model, 'Span')
        expected = 4.57
        self.assertTrue(abs(expected - span) / expected < 1e-3)

class Props(unittest.TestCase):
    def test_resolve(self):
        url = astronautix.resolve('flox')
    
    def test_query(self):
        url = astronautix.resolve('flox')
        model = astronautix.query(url)
        Isp_sl = astronautix.getValue(model, 'Specific impulse sea level')
        expected = 316.0
        self.assertTrue(abs(expected - Isp_sl) / expected < 1e-3)

if __name__ == '__main__':
    unittest.main()
