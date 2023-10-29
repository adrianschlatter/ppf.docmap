# -*- coding: utf-8 -*-

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import io
import urllib.request
import urllib.parse
import urllib.error
import pdfx
import regex as re
from pathlib import Path
import logging

from .utils import export
from .exceptions import OpeningError

logger = logging.getLogger('.filescanners')


@export
class Registry(type):
    registry = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super(Registry, cls).__new__(cls, name, bases, attrs)
        cls.registry[new_cls.mimetype] = new_cls

        return new_cls


@export
class FileScanner(metaclass=Registry):
    mimetype = '*'
    _ref_keys = {}

    def __init__(self, jabref_keys=None):
        self.jabref_keys = jabref_keys

    def __call__(self, filename):
        raise NotImplementedError()

    @property
    def ref_keys(self):
        return self._ref_keys

    def ref_keys_update(self, dct):
        self._ref_keys.update(dct)


@export
class DOCXScanner(FileScanner):
    mimetype = \
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    def __init__(self, jabref_keys=None):
        super().__init__(jabref_keys)

    def __call__(self, url):
        logger.info('Scanning %s', url)
        try:  # let's assume url is a URL and hope for the best
            logger.info('Opening %s', url)
            response = urllib.request.urlopen(url)
            buffer = io.BytesIO(response.read())
        except ValueError:  # URL-assumption does not work. Maybe it's a path?
            logger.info('Opening %s', urllib.parse.unquote(url))
            buffer = open(urllib.parse.unquote(url), 'rb')
        except urllib.error.URLError:
            raise OpeningError()

        logger.info('Parsing %s', url)
        document = Document(buffer)
        rels = document.part.rels
        return [rels[relname].target_ref
                for relname in rels
                if rels[relname].reltype == RT.HYPERLINK]


@export
class PDFScanner(FileScanner):
    mimetype = 'application/pdf'

    def __init__(self, jabref_keys=None):
        super().__init__(jabref_keys)

    def __call__(self, url):
        logger.info('Scanning %s', url)
        if url.find('file:') == 0:
            url = urllib.parse.unquote(url[5:])
        try:
            logger.info('Opening %s', url)
            pdf = pdfx.PDFx(url)
        except pdfx.DownloadError:
            raise OpeningError()
        else:
            urls = sum(pdf.get_references_as_dict().values(), [])
            return urls


@export
class MDScanner(FileScanner):
    mimetype = 'text/markdown'
    pttrn = re.compile(
        r"""
        (?<TEXT>                # TEXT group, including square brackets
        \[
            (?>                 # atomic group, perf. improvement
                [^\[\]]+        # any char except closing square bracket
                |               # OR
                (?&TEXT)        # recursively another pattern with opening
                                # and closing square brackets
            )*
        \]
        )
        (?:
            \(
                (?<URL>         # URL group
                    \S*?        # non-greedy non-whitespace characters
                )
                (?:             # non-capturing group: Need it just because
                                # we want to mark it as optional at the end
                    [ ]         # a space
                    "           # "
                    (?<TITLE>   # TITLE group
                        (?:
                            [^"]        # non-quote chars
                            |           # OR
                            (?<=\\)"    # " preceded by \ (escaped quote)
                        )*?
                    )
                    "           # "
                )?              # title part is optional
            \)
        )
        """, flags=re.X)

    def __init__(self, jabref_keys=None):
        super().__init__(jabref_keys)

    def __call__(self, link):
        logger.info('Scanning %s', link)
        # 'link' can be a URL or a path:
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme in ['file', '']:
            path = (Path(urllib.parse.unquote(parsed.netloc)) /
                    Path(urllib.parse.unquote(parsed.path)))
            logger.info('Opening %s', path)
            with open(path, 'r') as f:
                text = f.read()
        else:
            logger.info('Opening %s', link)
            response = urllib.request.urlopen(link)
            raw = response.read()
            text = raw.decode(response.headers.get_content_charset())

        return [match['URL'] for match in self.pttrn.finditer(text)]


@export
class HTMLScanner(FileScanner):
    mimetype = 'text/html'
    pttrn = re.compile(
        r"""
        <a\s+(?:[^>]*?\s+)?href=        # <a href=
            (?:
                (?:                     # non-" inside ""
                    "
                    (?P<LINK_DQ>        # non-" or escaped "
                        (?:
                            [^"]
                            |
                            (?<=\\)"
                         )*
                    )
                    "
                 )
                 |
                 (?:                    # non-' inside ''
                    '
                    (?P<LINK_SQ>        # non-' or escaped '
                        (?:
                            [^']
                            |
                            (?<=\\)'
                        )*
                    )
                    '
                 )
             )
        """, flags=re.X)

    def __init__(self, jabref_keys=None):
        super().__init__(jabref_keys)

    def __call__(self, link):
        logger.info('Scanning %s', link)
        # 'link' can be a URL or a path:
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme in ['file', '']:
            path = (Path(urllib.parse.unquote(parsed.netloc)) /
                    Path(urllib.parse.unquote(parsed.path)))
            logger.info('Opening %s', path)
            with open(path, 'r') as f:
                text = f.read()
        else:
            response = urllib.request.urlopen(link)
            logger.info('Opening %s', link)
            raw = response.read()
            text = raw.decode(response.headers.get_content_charset())

        return [match.groupdict()['LINK_DQ'] if 'LINK_DQ' in match.groupdict()
                else match.groupdict()['LINK_SQ']
                for match in self.pttrn.finditer(text)]
