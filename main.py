import subprocess, sys
from sys import platform

if __name__ == '__main__':
  if platform == 'darwin':
    p = subprocess.Popen(
      ['/usr/local/bin/scrapy', 'crawl', 'weibosearch', '-a', 'username=%s:%s' % (sys.argv[1], sys.argv[2])])
  elif platform == 'linux':
    p = subprocess.Popen(['scrapy', 'crawl', 'weibosearch', '-a', 'username=%s:%s' % (sys.argv[1], sys.argv[2])])
  else:
    p = subprocess.Popen(['scrapy.bat', 'crawl', 'weibosearch', '-a', 'username=%s:%s' % (sys.argv[1], sys.argv[2])])
  output = p.communicate()[0]
  print output
