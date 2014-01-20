#!/usr/bin/env python

import sys
import urllib2
import re
from collections import defaultdict
from collections import deque

#First argument on the command line is the starting domain.
root = sys.argv[1]

#Page requests appear to only work if the protocol is included.
root_domain = None
if not re.search(r'://', root):
  root_domain = "http://" + root
else:
  root_domain = root

#Class for crawling a page.
class PageCrawl:
  #Initialize with dictionaries encoding the incoming and outgoing
  #links as well as the root domain
  def __init__(self, forward_refs, back_refs, root_domain):
    self.forward_refs = forward_refs
    self.back_refs = back_refs
    self.root_domain = root_domain
    if self.root_domain[-1] == "/":
      self.root_domain = self.root_domain[0:-1]

  #A function to crawl a page and find all outgoing links
  def crawl(self, root):
    text = None
    try:
      request = urllib2.Request(root)
      responce = urllib2.urlopen(request)
      text = responce.read()
    except Exception as e:
      #print "ERROR:", e
      return 1

    if not responce or responce.getcode() != 200:
      return 1

    #Find all href links in the page.
    urls = re.findall(r'<a[^>]*href=[\'"]+([^\'" >]+)', text)

    next_urls = []
    for u in urls:
      url = None
      if u[0] == '/':
        url = self.root_domain + u
      elif u[0:2] == './':
        url = self.root_domain + u[1:len(u)] #Remove the '.' from ./ paths
      elif u[0] == '?':
        url = self.root_domain + u
      elif u[0] == '#':
        continue # Don't follow anchor links
      elif u[0:10] == "javascript":
        continue # Don't examine javascript
      else:
        url = u
      next_urls.append(url)
      self.forward_refs[root].append(url) #Outgoing link
      self.back_refs[url].append(root)    #Incoming link

    return next_urls

#Class to manage crawling pages using a breadth first search
class CrawlDispatcher:
  #Initialize with a PageCrawl object that will be used to crawl pages
  def __init__(self, page_crawl):
    #self.forward_refs = forward_refs
    #self.back_refs = back_refs
    self.page_crawl = page_crawl
    self.queue = deque()
    self.visited = []

  #Function to crawl a domain. Note that currently your start page is the root
  #page of the domain.
  def crawl_domain(self, start):
    self.queue.append(start)

    #Remove trailing slash from the domain.
    domain = re.findall(r'(?:http://)?(.*)', start)[0]
    if domain[-1] == "/":
      domain = domain[0:-1]

    #While there are still pages in the queue take them (FIFO) and
    #crawl from them.
    while self.queue:
      element = self.queue.popleft()
      #We are only walking the domain, not the entire internet.
      #Note that this could walk external pages if the domain is an
      #argument in the url
      if not domain in element:
        continue
      #Crawl the page
      url_list = self.page_crawl.crawl(element)
      if url_list == 1:
        continue
      try:
        for u in url_list:
          if not u in self.visited:
            self.queue.append(u)
            self.visited.append(u)
      except Exception as e:
        print "Error code crawling page:", url_list
        print "Page:", element
        exit(1)

#Forward and back link dicts. Pagecrawl object to crawl website and
#a CrawlDispatcher object to manage crawling the domain.
forward_links = defaultdict(list)
back_links = defaultdict(list)
pc = PageCrawl(forward_links, back_links, root_domain)
cd = CrawlDispatcher(pc)

cd.crawl_domain(root_domain)


# Print each link in site. Currently disabled since it is
# incredibly noisy.
#for key in forward_links.keys():
#  for e in forward_links[key]:
#    print key, "=>", e


# Sort the incoming link map by negative number of incoming links and print
# from the most linked pages to the least linked pages.
# Note: Negative len so that more links is earlier in list
print "Incoming link count:"
pop_list = sorted(forward_links.keys(), key=lambda e:-len(forward_links[e]))
for e in pop_list:
  print len(forward_links[e]), ":", e


exit(0)
