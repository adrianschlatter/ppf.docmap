# -*- coding: utf-8 -*-
"""
Unittests for Crawler
"""

import unittest
from pathlib import Path
import ppf.docmap as dmap

THIS_DIR = Path(__file__).parent


class Test_Crawler(unittest.TestCase):

    def setUp(self):
        self.crawl = dmap.Crawler()

    def test_docA(self):
        url = (THIS_DIR / Path('data/Document A.md')).absolute().as_uri()
        self.crawl(url, depth=1)

        self.assertEqual(set(self.crawl.tree.visited_urls),
                         {((THIS_DIR / 'data' / 'Document A.md')
                           .absolute().as_uri()),
                          './Document%20C.docx'})
