# -*- coding: utf-8 -*-
"""
Unittests for DOCXScanner
"""

import unittest
from pathlib import Path
import ppf.docmap as dmap

THIS_DIR = Path(__file__).parent


class Test_DOCX(unittest.TestCase):

    def setUp(self):
        self.scan = dmap.DOCXScanner()

    def test_docB(self):
        url = (THIS_DIR / Path('data/Document B.docx')).absolute().as_uri()
        links = self.scan(url)

        self.assertEqual(set(links),
                         {'Document%20C.docx',
                         'https://github.com/adrianschlatter/ppf.datamatrix'})
