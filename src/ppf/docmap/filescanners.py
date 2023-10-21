# -*- coding: utf-8 -*-

from .utils import export
from .exceptions import OpeningError

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import io
import urllib.request
import urllib.parse
import urllib.error
import pdfx
import regex as re
from pathlib import Path


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
        try:  # let's assume url is a URL and hope for the best
            response = urllib.request.urlopen(url)
            buffer = io.BytesIO(response.read())
        except ValueError:  # URL-assumption does not work. Maybe it's a path?
            buffer = open(urllib.parse.unquote(url), 'rb')
        except urllib.error.URLError:
            raise OpeningError()

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
        if url.find('file:') == 0:
            url = urllib.parse.unquote(url[5:])
        try:
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
        # 'link' can be a URL or a path:
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme in ['file', '']:
            path = (Path(urllib.parse.unquote(parsed.netloc)) /
                    Path(urllib.parse.unquote(parsed.path)))
            with open(path, 'r') as f:
                text = f.read()
        else:
            response = urllib.request.urlopen(link)
            raw = response.read()
            text = raw.decode(response.headers.get_content_charset())

        return [match['URL'] for match in self.pttrn.finditer(text)]
