# File Scanners

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

