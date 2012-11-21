#-*- coding: utf-8 -*-
# A weibo parser.
#
# tpeng <pengtaoo@gmail.com>
# 2012/9/21
#
from pyquery import PyQuery as pq
from datetime import datetime
import re

class SearchPage():
  def __init__(self, values):
    if values is None or len(values) == 0:
      self.values = []
    else:
      self.values = values

  def __len__(self):
    return len(self.values)

  def __getitem__(self, key):
    return self.values[key]

  def __iter__(self):
    return iter(self.values)

  @staticmethod
  def wrap(html):
    jQuery = pq(html)
    hrefs = jQuery('li a')
    values = []
    if len(hrefs) > 1:
      size = int(hrefs[-2].text)
      href = hrefs[-2]
      link = href.get('href')
      if link.startswith('/'):
        link = '%s%s' % ('http://s.weibo.com', link)
      for i in xrange(1, size + 1):
        values.append(re.sub(r'page=\d+', 'page=%s' % i, link))
    return SearchPage(values)

# represent a single feed return by the weibo search
class Author():
  def __init__(self, id, name, img_url):
    self.id = id
    self.name = name
    self.img_url = img_url

  @staticmethod
  def wrap(html):
    jQuery = pq(html)
    name = unicode(jQuery('a').attr('title'))
    img = jQuery('a img').attr('src')
    #    id = unicode(jQuery('a').attr('suda-data').split(':')[-1])
    id = re.search('id=(\d+)&', jQuery('a img').attr('usercard'), re.I).group(1)
    return Author(id, name, img)

  def __str__(self):
    return 'Author(id=%s, name=%s)' % (self.id, self.name)


class Feed():
  def __init__(self, mid, author, content, retweets, replies, timestamp):
    self.mid = mid
    self.author = author
    self.content = content
    self.retweets = retweets
    self.replies = replies
    self.timestamp = timestamp

  @staticmethod
  def wrap(html):
    replies = retweets = 0
    jQuery = pq(html)
    dl = jQuery("dl.feed_list")
    author = Author.wrap(dl('dt.face').html())
    em = jQuery('dd.content em').eq(0)
    imgs = em.find('img')
    # replace the images with image's alt text
    for img in imgs:
      if pq(img).attr('alt'):
        pq(img).replaceWith(pq(img).attr('alt'))
    spans = em.find('span')
    # replace the span (added by weibo search for highlight the words) with text
    for span in spans:
      pq(span).replaceWith(pq(span).text())
    content = em.text()
    info = jQuery('dd.content p.info').text()
    retweets_match = re.search(ur'\u8f6c\u53d1\((\d+)\)', info, re.M | re.I | re.U)
    if retweets_match:
      retweets = int(retweets_match.group(1))
    replies_match = re.search(ur'\u8bc4\u8bba\((\d+)\)', info, re.M | re.I | re.U)
    if replies_match:
      replies = int(replies_match.group(1))

    time = jQuery('dd.content p.info a.date').attr('date')
    timestamp = datetime.fromtimestamp(long(time) / 1000)
    return Feed(dl.attr('mid'), author, content, retweets, replies, timestamp)

  def __str__(self):
    return 'Feed(mid=%s author=%s)' % (self.mid, self.author)
