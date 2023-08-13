# -*- coding: utf-8 -*-
"""
Unittests for MDScanner
"""

import unittest
from pathlib import Path
import ppf.docmap as dmap

THIS_DIR = Path(__file__).parent


class Test_MD(unittest.TestCase):

    def setUp(self):
        self.scan = dmap.MDScanner()

    def test_docD(self):
        url = (THIS_DIR / Path('data/Document D.md')).absolute().as_uri()
        links = self.scan(url)

        self.assertEqual(set(links),
                         {'https://github.com/adrianschlatter/threadlib',
                          'https://github.com/adrianschlatter/ppf.datamatrix',
                          'https://github.com/adrianschlatter/ppf.jabref',
                          'https://github.com/adrianschlatter/webref',
                          'https://github.com/adrianschlatter/pyConic',
                          'https://github.com/adrianschlatter/tanuna',
                          'https://github.com/adrianschlatter/notebooks',
                          'https://github.com/adrianschlatter/ppf.noisetools',
                          'https://github.com/adrianschlatter/ppf.noisetools',
                          'https://github.com/adrianschlatter/ppf.electronics',
                          'https://github.com/adrianschlatter/rst4html',
                          'https://github.com/adrianschlatter/depaper',
                          'https://github.com/adrianschlatter/tmux.config',
                          'https://github.com/adrianschlatter/zsh.config',
                          'https://github.com/adrianschlatter/vimrc',
                          'https://github.com/adrianschlatter/ppf.sample'})
