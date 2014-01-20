#!/usr/bin/env python

import sys
import urllib2
import re
from collections import defaultdict
from collections import deque

#First argument on the command line is the starting domain.
root = sys.argv[1]

root_domain = None
if not re.search(r'://', root):
  root_domain = "http://" + root
else:
  root_domain = root

class PageCrawl:
  def __init__(self, forward_refs, back_refs, root_domain):
    self.forward_refs = forward_refs
    self.back_refs = back_refs
    self.root_domain = root_domain
    if self.root_domain[-1] == "/":
      self.root_domain = self.root_domain[0:-1]

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

    urls = re.findall(r'<a[^>]*href=[\'"]+([^\'" >]+)', text)

    next_urls = []
    for u in urls:
      url = None
      if u[0] == '/':
        url = self.root_domain + u
      elif u[0:2] == './':
        url = self.root_domain + u[1:len(u)]
      elif u[0] == '?':
        url = self.root_domain + u
      elif u[0] == '#':
        continue # Don't follow anchor links
      elif u[0:10] == "javascript":
        continue # Don't examine javascript
      else:
        url = u
      next_urls.append(url)
      self.forward_refs[root].append(url)
      self.back_refs[url].append(root)

    return next_urls

class CrawlDispatcher:
  def __init__(self, forward_refs, back_refs, page_crawl):
    self.forward_refs = forward_refs
    self.back_refs = back_refs
    self.page_crawl = page_crawl
    self.queue = deque()
    self.visited = []

  def crawl_domain(self, start):
    self.queue.append(start)

    domain = re.findall(r'(?:http://)?(.*)', start)[0]
    if domain[-1] == "/":
      domain = domain[0:-1]

    while self.queue:
      element = self.queue.popleft()
      if not domain in element:
        continue
      url_list = self.page_crawl.crawl(element)
      if url_list == 1:
        continue
      try:
        for u in url_list:
          if not u in self.visited:
            self.queue.append(u)
            self.visited.append(u)
      except Exception as e:
        print "url_list is int:", url_list
        print "element:", element
        exit(1)


site_map = defaultdict(list)
linked_to_map = defaultdict(list)
pc = PageCrawl(site_map, linked_to_map, root_domain)
cd = CrawlDispatcher(site_map, linked_to_map, pc)

cd.crawl_domain(root_domain)


# Print each link in site. Currently disabled since it is
# incredibly noisy.
#for key in site_map.keys():
#  for e in site_map[key]:
#    print key, "=>", e


# Sort the incoming link map by negative number of incoming links and print
# from the most linked pages to the least linked pages.
# Note: Negative len so that more links is earlier in list
print "Link count:"
pop_list = sorted(linked_to_map.keys(), key=lambda e:-len(linked_to_map[e]))
for e in pop_list:
  print len(linked_to_map[e]), ":", e


exit(0)
