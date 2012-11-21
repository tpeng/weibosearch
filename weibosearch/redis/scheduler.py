import redis
from weibosearch.redis.queue import SpiderQueue
from weibosearch.redis.dupefilter import RFPDupeFilter

# default values
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
SCHEDULER_PERSIST = True
QUEUE_KEY = '%(spider)s:requests'
DUPEFILTER_KEY = '%(spider)s:dupefilter'

class Scheduler(object):
  """Redis-based scheduler"""

  def __init__(self, redis, persist, queue_key):
    self.server = redis
    self.persist = persist
    self.queue_key = queue_key
    # in-memory queue
    self.own_queue = []

  def __len__(self):
    return len(self.queue)

  @classmethod
  def from_settings(cls, settings):
    host = settings.get('REDIS_HOST', REDIS_HOST)
    port = settings.get('REDIS_PORT', REDIS_PORT)
    persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
    queue_key = settings.get('SCHEDULER_QUEUE_KEY', QUEUE_KEY)
    server = redis.Redis(host, port)
    return cls(server, persist, queue_key)

  def open(self, spider):
    self.spider = spider
    self.queue = SpiderQueue(self.server, spider, self.queue_key)
    self.df = RFPDupeFilter(self.server, DUPEFILTER_KEY % {'spider': spider.name})
    # notice if there are requests already in the queue
    if not self.persist:
      self.df.clear()
      self.queue.clear()

    if len(self.queue):
      spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

  def close(self, reason):
    pass

  def enqueue_request(self, request):
    if not request.dont_filter and self.df.request_seen(request):
      return
    if self.spider.logined:
      self.queue.push(request)
    else:
      self.own_queue.append(request)

  def next_request(self):
    if self.spider.logined:
      return self.queue.pop()
    if len(self.own_queue) > 0:
      return self.own_queue.pop()

  def has_pending_requests(self):
    if self.spider.logined:
      return len(self) > 0
    return len(self.own_queue)

