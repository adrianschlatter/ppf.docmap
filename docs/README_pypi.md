# ppf.docmap

ppf.docmap is a python package to find links in documents and to crawl
documents to map dependencies between them.

Check out the project website to find out  more!

# Installation

ppf.docmap needs python-magic. python-magic is installed automatically by
pip if you do not already have it. However, python-magic depends on the
system's libmagic which needs to be installed separately. Here's how to do
that:

## Debian/Ubuntu

```
sudo apt-get install libmagic1
```

## Windows

You'll need DLLs for libmagic. @julian-r maintains a pypi package with
the DLLs, you can fetch it with:

```
pip install python-magic-bin
```

## OSX

When using Homebrew:

```
brew install libmagic
```

When using macports:

```
port install file
```
