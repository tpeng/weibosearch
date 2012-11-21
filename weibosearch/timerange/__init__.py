# tpeng: from https://github.com/charettes/python-timerange @c7ccf80038e2894b8108999b745697283a7945d4
# maybe use git submodule is a better idea?

from datetime import time, date, datetime

__all__ = ('datetimerange', 'daterange', 'timerange')

class temporalrange:
  def __init__(self, frm, to):
    if not isinstance(frm, self.temporal):
      raise TypeError("frm must be an instance of %s" % self.temporal.__name__)

    if not isinstance(to, self.temporal):
      raise TypeError("to must be an instance of %s" % self.temporal.__name__)

    self.frm, self.to = sorted([frm, to])

  def intersection(self, range):
    if not isinstance(range, self.__class__):
      raise TypeError("can only apply intersections between two instances of %s" %\
                      self.__class__.__name__)

    frm = max(self.frm, range.frm)
    to = min(self.to, range.to)

    if frm > to:
      return None
    else:
      return self.__class__(frm, to)

  __and__ = intersection

  def include(self, range):
    """Test if the range is contained within this one"""
    return range.frm >= self.frm and range.to <= self.to

  def delta(self):
    """Fetch the datetime.timedelta between self.frm and self.to"""
    return self.to - self.frm

  def __contains__(self, item):
    if not isinstance(item, self.temporal):
      raise TypeError("a %s only contains instances of %s" % (self.__class__.__name__,
                                                              self.temporal.__name__))

    return item >= self.frm and item <= self.to

  def __eq__(self, other):
    if not isinstance(other, self.__class__):
      return NotImplemented
    return self.to == other.to and self.frm == other.frm

  def __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    return hash(repr(self))

  def __repr__(self):
    return "timerange.%s(%s, %s)" % (self.__class__.__name__, repr(self.frm), repr(self.to))


class datetimerange(temporalrange):
  """

  >>> a = datetime(2010, 5, 14, 23)
  >>> b = datetime(2010, 5, 15)
  >>> c = datetime(2010, 5, 15, 3)
  >>> d = datetime(2010, 5, 16)
  >>> e = datetime(2010, 5, 17)

  >>> datetimerange(a, 12)
  Traceback (most recent call last):
      ...
  TypeError: to must be an instance of datetime

  >>> datetimerange(b, a).frm == a
  True

  >>> hash(datetimerange(a, b)) == hash(datetimerange(a, b))
  True

  >>> repr(datetimerange(a, b))
  'timerange.datetimerange(datetime.datetime(2010, 5, 14, 23, 0), datetime.datetime(2010, 5, 15, 0, 0))'

  >>> datetimerange(a, b).delta()
  datetime.timedelta(0, 3600)

  >>> a == datetime(2010, 5, 14, 23)
  True

  >>> a == b
  False

  >>> b in datetimerange(a, c)
  True

  >>> c in datetimerange(a, b)
  False

  >>> 2 in datetimerange(a, c)
  Traceback (most recent call last):
      ...
  TypeError: a datetimerange only contains instances of datetime

  >>> c in datetimerange(a, d) & datetimerange(b, e)
  True

  >>> datetimerange(a, b) & datetimerange(d, e)

  >>> datetimerange(a, d).include(datetimerange(a, c))
  True

  >>> datetimerange(a, c).include(datetimerange(a, d))
  False
  """
  temporal = datetime


class daterange(temporalrange):
  """

  >>> a = date(2010, 5, 14)
  >>> b = date(2010, 5, 15)
  >>> c = date(2010, 5, 17)
  >>> d = date(2010, 5, 18)
  >>> e = date(2010, 5, 19)

  >>> daterange(a, 12)
  Traceback (most recent call last):
      ...
  TypeError: to must be an instance of date

  >>> daterange(b, a).frm == a
  True

  >>> hash(daterange(a, b)) == hash(daterange(a, b))
  True

  >>> repr(daterange(a, b))
  'timerange.daterange(datetime.date(2010, 5, 14), datetime.date(2010, 5, 15))'

  >>> daterange(a, b).delta()
  datetime.timedelta(1)

  >>> a == date(2010, 5, 14)
  True

  >>> a == b
  False

  >>> b in daterange(a, c)
  True

  >>> c in daterange(a, b)
  False

  >>> 2 in daterange(a, c)
  Traceback (most recent call last):
      ...
  TypeError: a daterange only contains instances of date

  >>> c in daterange(a, d) & daterange(b, e)
  True

  >>> daterange(a, b) & daterange(d, e)

  >>> daterange(a, d).include(daterange(a, c))
  True

  >>> daterange(a, c).include(daterange(a, d))
  False
  """
  temporal = date


class timerange(temporalrange):
  """

  >>> a = time(12, 15)
  >>> b = time(12, 25)
  >>> c = time(13, 40)
  >>> d = time(16, 20)
  >>> e = time(18, 50)

  >>> timerange(a, 12)
  Traceback (most recent call last):
      ...
  TypeError: to must be an instance of time

  >>> timerange(b, a).frm == a
  True

  >>> hash(timerange(a, b)) == hash(timerange(a, b))
  True

  >>> repr(timerange(a, b))
  'timerange.timerange(datetime.time(12, 15), datetime.time(12, 25))'

  >>> timerange(a, b).delta()
  datetime.timedelta(0, 600)

  >>> a == time(12, 15)
  True

  >>> a == b
  False

  >>> b in timerange(a, c)
  True

  >>> c in timerange(a, b)
  False

  >>> 2 in timerange(a, c)
  Traceback (most recent call last):
      ...
  TypeError: a timerange only contains instances of time

  >>> c in timerange(a, d) & timerange(b, e)
  True

  >>> timerange(a, b) & timerange(d, e)

  >>> timerange(a, d).include(timerange(a, c))
  True

  >>> timerange(a, c).include(timerange(a, d))
  False
  """
  temporal = time

  #@staticmethod
  def __datetime(time):
    return datetime.min.replace(
      hour=time.hour,
      minute=time.minute,
      second=time.second,
      microsecond=time.microsecond,
      tzinfo=time.tzinfo
    )

  __datetime = staticmethod(__datetime)

  def delta(self):
    return timerange.__datetime(self.to) - timerange.__datetime(self.frm)

if __name__ == "__main__":
  import doctest

  doctest.testmod()
