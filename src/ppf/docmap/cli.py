# -*- coding: utf-8 -*-

from plumbum import cli
from pkg_resources import get_distribution
from ppf.docmap import mimetype, FileScanner, Crawler
from sys import stdout
from os import linesep, getcwd
from urllib.parse import urlparse, urljoin, quote


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

    def main(self, doc):
        parsed = urlparse(doc)
        if parsed.scheme == '':
            # convert path to URL:
            url = urljoin(f'file://{getcwd()}/', quote(doc))

        crawl = Crawler()

        if self.abs_urls:
            def action(node):
                print('    ' * node.level + node.abs_url())
        else:
            def action(node):
                print('    ' * node.level + node.url)

        crawl(url, depth=self.level, action=action)


def main():
    DocMapp.run()


if __name__ == '__main__':
    main()
