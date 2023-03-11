# -*- coding: utf-8 -*-
"""
Unittests
"""

import unittest
import ppf.docmap as dmap


class Smoke_Test():
    """Template class to test for unexpected exceptions."""

    def setUp(self):
        """
        Implement in Child class to setUp instance of your class
        as self.scanner.
        """
        pass

    def test_call(self):
        """Call scanner with invalid url."""

        with self.assertRaises(dmap.OpeningError):
            self.scanner('https://fantasy.url.net')


class Test_DOCXScanner(Smoke_Test, unittest.TestCase):
    """Smoke test DOCXScanner"""

    def setUp(self):
        try:
            self.scanner = dmap.DOCXScanner()
        except:
            self.fail('Exception upon valid instantiation')


class Test_PDFScanner(Smoke_Test, unittest.TestCase):
    """Smoke test PDFScanner."""

    def setUp(self):
        try:
            self.scanner = dmap.PDFScanner()
        except:
            self.fail('Exception upon valid instantiation')


if __name__ == '__main__':
    # This enables running the unit tests by running this script which is
    # much more convenient than 'python setup.py test' while developing tests.
    # Note: package-under-test needs to be in python-path
    unittest.main()
