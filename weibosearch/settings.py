# Scrapy settings for scrapy_weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'weibosearch'
BOT_VERSION = '0.1'

SPIDER_MODULES = ['weibosearch.spiders']
NEWSPIDER_MODULE = 'weibosearch.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

# redis config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# schduler config
SCHEDULER_PERSIST = True
QUEUE_KEY = '%(spider)s:requests'
DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER = "weibosearch.redis.scheduler.Scheduler"

# pipelines config
ITEM_PIPELINES = ['weibosearch.pipelines.ScrapyWeiboPipeline']

DOWNLOAD_DELAY = 30

LOG_LEVEL = 'INFO'

#LOG_FILE = 'log.txt'

TIME_DELTA = 30

# bootstrap from file (item.txt) or from db
BOOTSTRAP = 'file'

# how many feeds can fetch from a item
FEED_LIMIT = 200000