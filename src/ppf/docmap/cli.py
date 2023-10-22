# -*- coding: utf-8 -*-

from plumbum import cli
from pkg_resources import get_distribution
from ppf.docmap import mimetype, FileScanner, Crawler
from sys import stdout
from os import linesep


class DocMapp(cli.Application):
    PROGNAME = 'docmap'
    VERSION = get_distribution('ppf-docmap').version
    verbose = cli.Flag(['v', 'verbose'],
                       help='If given, I will be very talkative')


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

    def main(self, doc):
        crawl = Crawler()
        crawl(doc)


def main():
    DocMapp.run()


if __name__ == '__main__':
    main()
