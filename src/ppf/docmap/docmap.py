# -*- coding: utf-8 -*-

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import magic
import urllib
import io
import pdfx
import graphviz
from .utils import export
from .exceptions import OpeningError


@export
class FileScanner():
    def __init__(self, jabref_keys=None):
        self.jabref_keys = jabref_keys

    def __call__(self, filename):
        raise NotImplementedError()


@export
class DOCXScanner(FileScanner):
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
class Crawler():
    scan_class_reg = {
        'application/vnd.openxmlformats-officedocument'
        '.wordprocessingml.document': DOCXScanner,
        'application/pdf': PDFScanner}
    scan_reg = {}

    def __init__(self):
        self.visited_urls = []
        self.dot = graphviz.Digraph()
        for mime in self.scan_class_reg.keys():
            self.scan_reg[mime] = self.scan_class_reg[mime]()

    def __call__(self, url):
        url_hash = str(0)
        self.visited_urls = [url]
        self.dot.node(url_hash)
        scan_func = self.scan_reg.get(mimetype(url), lambda url: [])
        self._crawl(scan_func(url), origin=url_hash, indent=4)

    def _crawl(self, urls, origin='', indent=0):
        for url in urls:
            print(' '*indent + url)
            if url in self.visited_urls:
                url_hash = str(self.visited_urls.index(url))
                self.dot.edge(origin, url_hash)
                continue

            url_hash = str(len(self.visited_urls))
            self.visited_urls.append(url)
            self.dot.node(url_hash)
            self.dot.edge(origin, url_hash)

            scan_func = self.scan_reg.get(mimetype(url), lambda url: [])
            self._crawl(scan_func(url), origin=url_hash, indent=indent + 4)


@export
def mimetype(url):
    try:
        buffer = urllib.request.urlopen(url, timeout=10).read(4096)
    except urllib.error.URLError:
        return None
    else:
        mime = magic.from_buffer(buffer, mime=True)
        return mime
