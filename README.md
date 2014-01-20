h1. Python Webcrawler
==================================

This is a python application that will crawl a domain (starting at said domain) and find all links from the given page to every other reachable page in that sub domain.

To install and run the following steps are necessary:
1) git clone <location of git repo>
2) ./crawler.py <domain> > <out file>

The out file will consist of a list of the reachable pages in that domain and the number of incoming links each page has.
