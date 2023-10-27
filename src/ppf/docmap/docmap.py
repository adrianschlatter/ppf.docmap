# -*- coding: utf-8 -*-

import magic
import urllib
from urllib.parse import urlparse, urljoin
from pathlib import Path

from .utils import export
from .filescanners import FileScanner


class Node():
    """A Node of a (document-) Tree"""

    def __init__(self, url, parent=None):
        if parent is None and urlparse(url).scheme == '':
            raise ValueError('Root node must be an absolute URL')

        self.url = url
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

    def abs_url(self, url=None):
        """Determine absolute url of the node."""
        if url is None:
            if self.parent is None:
                return self.url
            else:
                return urljoin(self.parent.abs_url(), self.url)

        return urljoin(self.abs_url(), url)

    def find_abs_url(self, abs_url, searched=[]):
        """Find a node by its absolute url."""
        if self.abs_url() == abs_url:
            return self

        # stop if we already searched this node:
        # (can happen if the tree is not a tree but a graph)
        if self in searched:
            return None

        for child in self.children:
            node = child.find_abs_url(abs_url, searched=searched+[self])
            if node is not None:
                return node

        return None

    @property
    def level(self):
        """Level of the node in the tree."""
        if self.parent is None:
            return 0
        else:
            return self.parent.level + 1

    @property
    def visited_urls(self):
        """List of all visited URLs."""
        if len(self.children) == 0:
            return [self.url]
        else:
            return [self.url] + \
                    sum([child.visited_urls for child in self.children], [])

    @property
    def index(self):
        """Index of the node in the tree."""
        return [] if self.parent is None else \
            self.parent.index + [self.parent.children.index(self)]

    def __getitem__(self, index):
        """Get a child node by its index."""
        return self if index == [] else self.children[index[0]][index[1:]]


@export
class Crawler():
    scan_reg = {}

    def __init__(self):
        self.visited_urls = []
        for mime in FileScanner.registry.keys():
            self.scan_reg[mime] = FileScanner.registry[mime]()

    def __call__(self, abs_url, depth=None, action=lambda node: None):
        self.tree = Node(abs_url, parent=None)
        action(self.tree)

        if depth != 0:
            new_depth = depth - 1 if depth is not None else None
            # find correct scanner for the mimetype:
            scan = self.scan_reg.get(mimetype(abs_url), lambda abs_url: [])
            # scan and crawl:
            for link in scan(abs_url):
                self._crawl(link, origin=self.tree,
                            depth=new_depth, action=action)

        return self.tree

    def _crawl(self, url, origin, depth, action):
        abs_url = origin.abs_url(url)
        node = self.tree.find_abs_url(abs_url)

        if node is not None:  # node already exists in the tree
            origin.children.append(node)
            action(node)
            return

        node = Node(url, parent=origin)
        action(node)

        if depth != 0:
            new_depth = depth - 1 if depth is not None else None
            # find correct scanner for the mimetype:
            scan = self.scan_reg.get(mimetype(abs_url), lambda abs_url: [])
            # scan and crawl:
            for link in scan(abs_url):
                self._crawl(link, origin=node, depth=new_depth, action=action)


@export
def mimetype(link):
    # 'link' can be a URL or a path:
    parsed = urlparse(link)
    try:
        if parsed.scheme in ['file', '']:
            path = (Path(urllib.parse.unquote(parsed.netloc)) /
                    Path(urllib.parse.unquote(parsed.path)))
            with open(path, 'rb') as f:
                buffer = f.read(4096)
        else:
            response = urllib.request.urlopen(link, timeout=10)
            buffer = response.read(4096)
    except (FileNotFoundError, urllib.error.URLError):
        return None
    else:
        mime = magic.from_buffer(buffer, mime=True)
        if mime == 'text/plain':
            parsed = urllib.parse.urlparse(link)
            if Path(parsed.path).suffix == '.md':
                mime = 'text/markdown'

        return mime
