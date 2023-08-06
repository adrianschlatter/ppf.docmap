# -*- coding: utf-8 -*-
"""
ppf.docmap
++++++++++


ppf.docmap is a python package to find links in documents and to crawl
documents to map dependencies between them.
"""

__version__ = '0.1'

# import every function, class, etc. that should be visible in the package
from .docmap import *
from .filescanners import *
from .exceptions import *

del docmap
del filescanners
del exceptions
del utils
