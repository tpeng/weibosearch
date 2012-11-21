#coding=utf-8
# weibosearch spider
# tpeng <pengtaoo@gmail.com>
#
import codecs
from datetime import datetime, timedelta
import urllib
import MySQLdb
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.spider import BaseSpider
from weibosearch.feeds import SearchPage
from weibosearch.items import ScrapyWeiboItem
import re, json
from pyquery import PyQuery as pq
from lxml.html import tostring
from weibosearch.query import QueryFactory
from weibosearch.sina.weibo import Weibo
from weibosearch.sina import _epoch
from weibosearch.timerange import daterange

# default values
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

class WeiboSearchSpider(BaseSpider):
  name = 'weibosearch'
  allowed_domains = ['weibo.com']
  weibo = Weibo()

  def __init__(self, username=None):
    BaseSpider.__init__(self)
    self.username, self.pwd = username.split(':')
    self.db = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="pw", db="weibosearch2",
      charset='utf8', use_unicode=True)
    self.cursor = self.db.cursor()
    self.logined = False

    host = settings.get('REDIS_HOST', REDIS_HOST)
    port = settings.get('REDIS_PORT', REDIS_PORT)

    log.msg('login with %s' % self.username, level=log.INFO)
    login_url = self.weibo.login(self.username, self.pwd)
    if login_url:
      log.msg('login successful, start crawling.', level=log.INFO)
      self.start_urls.append(login_url)
    else:
      log.msg('login failed', level=log.ERROR)

  # only parse the login page
  def parse(self, response):
    if response.body.find('feedBackUrlCallBack') != -1:
      userinfo = json.loads(re.search(r'feedBackUrlCallBack\((.*?)\)', response.body, re.I).group(1))['userinfo']
      log.msg('user id %s' % userinfo['userid'], level=log.INFO)
      assert userinfo['userid'] == self.username
      self.logined = True

      bootstrap = settings.get('BOOTSTRAP')
      log.msg('bootstrap from %s' % bootstrap, level=log.INFO)
      # FIXME: use last scheduled time instead of today, otherwise queue filter will not work
      today = datetime.now()
      if bootstrap == 'file':
        lines = tuple(codecs.open('items.txt', 'r', 'utf-8'))
        for line in lines:
          if line.startswith("#"):
            continue
          start = _epoch()
          url = QueryFactory.create_timerange_query(urllib.quote(line.encode('utf8')), start, today)
          request = Request(url=url, callback=self.parsel_weibo)
          request.meta['query'] = line
          request.meta['start'] = start.strftime("%Y-%m-%d %H:%M:%S")
          request.meta['end'] = today.strftime("%Y-%m-%d %H:%M:%S")
          request.meta['last_fetched'] = today.strftime("%Y-%m-%d %H:%M:%S")
          yield request
      # TODO: can also bootstrap from db

  def parsel_weibo(self, response):
    query = response.request.meta['query']
    start = datetime.strptime(response.request.meta['start'], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(response.request.meta['end'], "%Y-%m-%d %H:%M:%S")
    range = daterange(start, end).delta()
    last_fetched = datetime.strptime(response.request.meta['last_fetched'], "%Y-%m-%d %H:%M:%S")

    jQuery = pq(response.body)
    scripts = jQuery('script')

    text = "".join(filter(lambda x: x is not None, [x.text for x in scripts]))

    # check if we exceed the sina limit
    sassfilter_match = re.search(r'{(\"pid\":\"pl_common_sassfilter\".*?)}', text, re.M | re.I)
    if sassfilter_match:
      raise CloseSpider('weibo search exceeded')

    # check the num of search results
    totalshow_match = re.search(r'{(\"pid\":\"pl_common_totalshow\".*?)}', text, re.M | re.I)
    if totalshow_match:
      html = json.loads(totalshow_match.group())['html']
      if len(html) == 0:
        raise CloseSpider('not login? %s' % html)
      totalshow = pq(html)
      if totalshow('div.topcon_num').html() is None:
        log.msg('%s 0 feeds' % query, level=log.INFO)
        return
      topcon_num = int(re.search('\s(\d+)\s', totalshow('div.topcon_num').text().replace(',', ''), re.I).group(1))
      log.msg('%s %d feeds' % (query, topcon_num), level=log.INFO)
      max_feeds = settings.getint('FEED_LIMIT', 200000)
      if topcon_num > max_feeds:
        log.msg('too much (%d) result for %s.' % (topcon_num, query), logLevel=log.WARNING)
      elif 1000 < topcon_num < max_feeds:
        # weibo search only allow 20 feeds on 1 page and at most 50 pages.
        days = range.days / float(2)
        middle = start + timedelta(days)

        # first part
        url = QueryFactory.create_timerange_query(urllib.quote(query.encode('utf8')), start, middle)
        request = Request(url=url, callback=self.parsel_weibo)
        request.meta['query'] = query
        request.meta['start'] = start.strftime("%Y-%m-%d %H:%M:%S")
        request.meta['end'] = middle.strftime("%Y-%m-%d %H:%M:%S")
        request.meta['priority'] = days / 2
        request.meta['last_fetched'] = last_fetched.strftime("%Y-%m-%d %H:%M:%S")
        yield request

        # second part
        url2 = QueryFactory.create_timerange_query(urllib.quote(query.encode('utf8')), middle, end)
        request2 = Request(url=url2, callback=self.parsel_weibo)
        request2.meta['query'] = query
        request2.meta['start'] = middle.strftime("%Y-%m-%d %H:%M:%S")
        request2.meta['end'] = end.strftime("%Y-%m-%d %H:%M:%S")
        request2.meta['priority'] = days / 2
        request2.meta['last_fetched'] = last_fetched.strftime("%Y-%m-%d %H:%M:%S")
        yield request2
      else:
        # check the feeds update
        feedlist_match = re.search(r'{(\"pid\":\"pl_weibo_feedlist\".*?)}', text, re.M | re.I)
        if feedlist_match:
          search_results = pq(json.loads(feedlist_match.group())['html'])
          feeds = search_results('dl.feed_list')
          search_pages = search_results('ul.search_page_M')
          pages = SearchPage.wrap(search_pages)

          # send the items to pipeline
          for feed in feeds:
            item = ScrapyWeiboItem()
            item['html'] = tostring(feed)
            yield item
            # skip first page and request other pages
          for i in xrange(2, len(pages)):
            query = pages[i]
            log.msg('%s' % query)
            request = Request(url=query, callback=self.parse_page)
            request.meta['query'] = query
            yield request

  # parse single weibo page
  def parse_page(self, response):
    jQuery = pq(response.body)
    scripts = jQuery('script')
    for script in scripts:
      match = re.search(r'{(\"pid\":\"pl_weibo_feedlist\".*)}', unicode(script.text), re.M | re.I)
      if match:
        search_results = pq(json.loads(match.group())['html'])
        feeds = search_results('dl.feed_list')
        for feed in feeds:
          item = ScrapyWeiboItem()
          item['html'] = tostring(feed)
          yield item



