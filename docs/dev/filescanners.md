# File Scanners

## DOCX Scanner

Hyperlinks in Word documents are - apparently - always URL encoded. This means,
for example, that the link "Document%20B.docx" refers to the file
"Document B.docx". If the document refered to *really* has the name
"Document%20B.docx" (i.e., no space), Word (16.78 for Mac) has a bug: It will
store "Document%20B.docx" as hyperlink.  When clicking the link, Word
assumes URL encoding, decodes the URL to "Document B.docx", and then complains
that the file does not exist.


## MarkDown Scanner

The MarkDown Scanner uses a regular expression to identify links. Michael
Perregrin has a
[nice article](https://www.michaelperrin.fr/blog/2019/02/advanced-regular-expressions)
on this topic. The regex we use in ppf.docmap looks like this (visualized using
[Debuggex](https://www.debuggex.com)):

![Markdown Link RegEx](https://www.debuggex.com/r/sdVuj7ZKX_9PaxTG)

It identifies the alternative text, the associated URL, and - if present - the
title text:

```
[alternative text](URL "title text")
```

For file scanning, we will only keep the URL part.

For now, I assume that links in markdown are url encoded. I am not sure this
is required by the standard, though. I do know that certain services also
accept non-urlencoded hyperlinks if they are enclosed in <...>.


# HTML Scanner

regex-type scanner based on this
[regex](https://www.debuggex.com/r/O5MAC7Adb4BF439l).
