"""Test cases for scraping technical data (listings and product information)
   from NewEgg.com
"""

import unittest
from scrapese import newegg

class Systems(unittest.TestCase):
    def test_resolve(self):
        url = newegg.resolve('Macbook Air')

    def test_query(self):
        url = newegg.resolve('Macbook Air')
        model = newegg.query(url)
        self.assertEquals(model['Interface'], 'USB 2.0')

class Processors(unittest.TestCase):
    def test_resolve(self):
        url = newegg.resolve('Devil Canyon', 'processors')

    def test_query(self):
        url = newegg.resolve('Devil Canyon', 'processors')
        model = newegg.query(url)
        self.assertEquals(model['L3 Cache'], '8MB')
        
class Memory(unittest.TestCase):
    def test_resolve(self):
        url = newegg.resolve('Corsair 16 GB', 'memory')

    def test_query(self):
        url = newegg.resolve('Corsair 16 GB', 'memory')
        model = newegg.query(url)
        self.assertEquals(model['Voltage'], '1.2V')

class Graphics(unittest.TestCase):
    def test_resolve(self):
        url = newegg.resolve('Windforce', 'graphics')

    def test_query(self):
        url = newegg.resolve('Windforce', 'graphics')
        model = newegg.query(url)
        self.assertEquals(model['Form Factor'], 'ATX')
        
if __name__ == '__main__':
    unittest.main()
   