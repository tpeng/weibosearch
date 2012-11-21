class QueryFactory:
  @staticmethod
  def create_query(query):
    return 'http://s.weibo.com/weibo/%s&Refer=STopic_box&scope=ori' % query

  @staticmethod
  def create_paging_query(query, page):
    return 'http://s.weibo.com/weibo/%s&page=%d' % (query, page)

  @staticmethod
  def create_timerange_query(query, start, end):
    s = start.strftime('%Y-%m-%d-%H')
    e = end.strftime('%Y-%m-%d-%H')
    return 'http://s.weibo.com/weibo/%s&Refer=STopic_box&timescope=custom:%s:%s&scope=ori' % (query, s, e)

