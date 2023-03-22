# -*- coding: utf-8 -*-

import magic
import urllib
import graphviz
from .utils import export
from .filescanners import FileScanner


@export
class Crawler():
    scan_reg = {}

    def __init__(self):
        self.visited_urls = []
        self.dot = graphviz.Digraph()
        for mime in FileScanner.registry.keys():
            self.scan_reg[mime] = FileScanner.registry[mime]()

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
