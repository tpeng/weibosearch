# See: http://doc.scrapy.org/en/0.14/topics/item-pipeline.html
# tpeng <pengtaoo@gmail.com>
#
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from weibosearch.feeds import Feed
from scrapy import log
import MySQLdb.cursors

class ScrapyWeiboPipeline(object):
  def __init__(self):
    self.dbpool = adbapi.ConnectionPool('MySQLdb',
      db='weibosearch2',
      user='root',
      passwd='pw',
      cursorclass=MySQLdb.cursors.DictCursor,
      charset='utf8',
      use_unicode=True
    )

  def process_item(self, item, spider):
    # run db query in thread pool
    if spider.savedb == 'True':
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
    return item

  def _conditional_insert(self, tx, item):
    # create record if doesn't exist.
    # all this block run on it's own thread
    try:
      feed = Feed.wrap(item['html'])
    except Exception as e:
      print e
      raise DropItem('Feed.wrap error: %s' % item['html'])

    # insert author
    tx.execute("select * from author where id = %s" % feed.author.id)
    result = tx.fetchone()
    if result:
      log.msg("Author already stored in db: %s" % feed.author.id, level=log.INFO)
    else:
      tx.execute("insert into author (id, name, url)"
                 "values (%s, %s, %s)",
        (feed.author.id, feed.author.name, feed.author.img_url))
      log.msg("Author stored in db: %s" % feed.author.id, level=log.INFO)

    # insert feed
    tx.execute("select * from feed where id = %s" % feed.mid)
    result = tx.fetchone()
    if result:
      log.msg("Feed already stored in db: (%s,%s)" % (feed.author.id, feed.mid), level=log.INFO)
    else:
      tx.execute("insert into feed (id, author_id, content, retweets, replies, timestamp)"
                 "values (%s, %s, %s, %s, %s, %s)",
        (feed.mid, feed.author.id, feed.content, feed.retweets, feed.replies,
         feed.timestamp.strftime('%Y-%m-%d %H:%M:%S')))

      log.msg("Feed stored in db: %s" % feed.mid, level=log.INFO)

  def handle_error(self, e):
    log.err(e)