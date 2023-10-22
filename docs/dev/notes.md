# Types of links

* absolute links (http://...)
* internal links (#something)
* relative links (./something.md)

Also, absolute links to internal sections of another document are possible.

urllib.parse.urlparse separates a URL into:

* scheme   (https://)
* netloc   (tambora.ch)
* path     (/photos/img_2043.jpg)
* params   (don't know)
* query    (ref_cta=Sign+up&amp;ref_loc=header+logged+out&amp;)
* fragment (start-of-content) [the # anchor]


# Handling of encodings

We have multiple encoding problems:

1. Encoding of the hyperlink string:
    * URL encoded?
    * something else?
2. Encoding of text files (e.g., .md):
    * ASCII?
    * Something else?

## Encoding of hyperlink strings

For now, we assume these are always URL encoded.


## Encoding of text files

What are our options to determine the encoding?

* Transfer protocol: http header may specify the type of encoding it is
  transmitting
* Header line in text file, e.g. "# -*- coding: utf-8 -*-"
* Tag inside text file, e.g., "<meta charset='utf-8'>"
* Guessing
