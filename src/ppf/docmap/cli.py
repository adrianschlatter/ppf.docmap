# -*- coding: utf-8 -*-

from plumbum import cli
from pkg_resources import get_distribution
from ppf.docmap import mimetype, FileScanner, Crawler
from sys import stdout
from os import linesep, getcwd
from urllib.parse import urlparse, urljoin, quote
import graphviz


class DocMapp(cli.Application):
    PROGNAME = 'docmap'
    VERSION = get_distribution('ppf-docmap').version
    verbose = cli.Flag(['v', 'verbose'])


@DocMapp.subcommand('ls')
class DocMappLs(cli.Application):
    """lists all references found in document"""

    def main(self, doc):
        # instantiate correct FileScanner class:
        scanner = FileScanner.registry[mimetype(doc)]()

        # scan document:
        refs = scanner(doc)
        for ref in refs:
            stdout.write(ref + linesep)


@DocMapp.subcommand('tree')
class DocMappTree(cli.Application):
    """hierarchically lists all references found in document"""

    level = cli.SwitchAttr(['L', 'level'], int, default=None,
                           help='Descend only level directories deep.')
    abs_urls = cli.Flag(['f'], help='Print the absolute URL of each link')
    graph = cli.Flag(['g', 'graphviz'], help='Output in graphviz format')

    def main(self, url):
        indices_graphed = []

        # closure to create graphviz graph:
        def to_graphviz(node):
            if node.index in indices_graphed:
                return

            indices_graphed.append(node.index)

            if self.abs_urls:
                dot.node(str(node.index), node.abs_url())
            else:
                dot.node(str(node.index), node.url)

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
        else:                                       # do live printing
            if self.abs_urls:                       # ... of absolute urls
                def action(node):
                    stdout.write('    ' * node.level +
                                 node.abs_url() + linesep)
            else:                                   # ... of relative urls
                def action(node):
                    stdout.write('    ' * node.level + node.url + linesep)

        crawl(url, depth=self.level, action=action)

        if self.graph:      # create graphviz graph
            dot = graphviz.Digraph()
            to_graphviz(crawl.tree)
            stdout.write(dot.source)


def main():
    DocMapp.run()


if __name__ == '__main__':
    main()
