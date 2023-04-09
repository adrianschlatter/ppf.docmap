# -*- coding: utf-8 -*-

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import io
import urllib
from .utils import export
from .exceptions import OpeningError
import pdfx


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
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.URLError:
            raise OpeningError()
        else:
            buffer = io.BytesIO(response.read())
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
