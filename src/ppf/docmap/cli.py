# -*- coding: utf-8 -*-

from plumbum import cli
from pkg_resources import get_distribution
from ppf.docmap import mimetype, FileScanner, Crawler
from sys import stdout, stderr
from os import linesep, getcwd
from urllib.parse import urlparse, urljoin, quote
import graphviz
import logging

from ppf.docmap.exceptions import OpeningError


logger = logging.getLogger('.cli')


class DocMapp(cli.Application):
    PROGNAME = 'docmap'
    VERSION = get_distribution('ppf-docmap').version
    verbose = cli.Flag(['v', 'verbose'])

    def main(self):
        if self.verbose:
            logging.basicConfig(level=logging.INFO)


@DocMapp.subcommand('ls')
class DocMappLs(cli.Application):
    """lists all references found in document"""

    def main(self, doc):
        logger.info('Scanning %s', doc)
        try:
            mime = mimetype(doc)
        except OpeningError:
            stderr.write(f'File not found: {doc}' + linesep)
            exit(1)

        logger.info('mimetype(%s): %s', doc, mime)
        # instantiate correct FileScanner class:
        scanner_class = FileScanner.registry.get(mime, None)
        scanner = scanner_class() if scanner_class else lambda abs_url: []
        # scan document:
        refs = scanner(doc)
        for ref in refs:
            stdout.write(ref + linesep)


@DocMapp.subcommand('tree')
class DocMappTree(cli.Application):
    """hierarchically lists all references found in document"""

    level = cli.SwitchAttr(['L', 'level'], int, default=None,
                           help='Descend only level directories deep.')
    graph = cli.Flag(['g', 'graphviz'], help='Output in graphviz format')
    naming = 'url'

    @cli.switch(['f'])
    def set_naming_abs_url(self):
        self.naming = 'abs_url'

    @cli.switch(['n', 'filename'])
    def set_naming_filename(self):
        self.naming = 'filename'

    def main(self, url):
        indices_graphed = []

        # closure to create graphviz graph:
        def to_graphviz(node):
            if node.index in indices_graphed:
                return

            indices_graphed.append(node.index)

            dot.node(str(node.index), getattr(node, self.naming)())

            if node.parent:
                dot.edge(str(node.parent.index), str(node.index))
            for child in node.children:
                to_graphviz(child)

        parsed = urlparse(url)
        if parsed.scheme == '':
            # convert path to URL:
            url = urljoin(f'file://{getcwd()}/', quote(url))

        crawl = Crawler()

        if self.graph:       # no live printing, will create a graph later
            def action(node):
                pass
        else:                # do live printing
            def action(node):
                stdout.write('    ' * node.level +
                             getattr(node, self.naming)() + linesep)

        crawl(url, depth=self.level, action=action)

        if self.graph:      # create graphviz graph
            dot = graphviz.Digraph('Document Map')
            dot.attr(layout='neato')
            dot.attr(overlap='false')
            to_graphviz(crawl.tree)
            stdout.write(dot.source)


def main():
    DocMapp.run()


if __name__ == '__main__':
    main()
