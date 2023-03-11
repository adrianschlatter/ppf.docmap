# -*- coding: utf-8 -*-
"""
Unittests for PDFScanner
"""

import unittest
from pathlib import Path
import ppf.docmap as dmap

THIS_DIR = Path(__file__).parent


class Test_PDF(unittest.TestCase):

    def setUp(self):
        self.scan = dmap.PDFScanner()

    def test_docB(self):
        url = (THIS_DIR / Path('data/Document B.pdf')).absolute().as_uri()
        links = self.scan(url)

        self.assertEqual(set(links),
                         {'Document%20C.docx',
                         'https://github.com/adrianschlatter/ppf.datamatrix'})
