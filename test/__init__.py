"""Defines the contents and execution interface for seres tests
"""

import importlib
import sys
import types
import unittest

if sys.version_info.major == 2:
	def is_test_case(c):
		return type(c) == types.TypeType and issubclass(c, unittest.TestCase)
else:
	def is_test_case(c):
		return isinstance(c, type) and issubclass(c, unittest.TestCase)

__all__ = [
    'ax',
    'ne'
]

def suite():
	ts = unittest.TestSuite()
	for test_module in __all__:
		m = importlib.import_module("scrapese.test." + test_module)
		for n in dir(m):
			c = getattr(m, n)
			if is_test_case(c):
				s = unittest.TestLoader().loadTestsFromTestCase(c)
				ts.addTests(s)
	return ts
				
if __name__ == "__main__":
	ttr = unittest.TextTestRunner(verbosity=3).run(suite())
	nTests = ttr.testsRun + len(ttr.skipped)
	print("Report:")
	print("\t" + str(len(ttr.failures)) + "/" + str(nTests) + " failed")
	print("\t" + str(len(ttr.errors)) + "/" + str(nTests) + " errors")
	print("\t" + str(len(ttr.skipped)) + "/" + str(nTests) + " skipped")
