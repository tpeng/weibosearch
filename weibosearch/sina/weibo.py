#coding=utf8
# original from http://www.douban.com/note/201767245/
# also see http://www.cnblogs.com/mouse-coder/archive/2013/03/03/2941265.html for recent change in weibo login
# modified by tpeng <pengtaoo@gmail.com>
# 2012/9/20

import urllib
import urllib2
import cookielib
import base64
import re, sys, json
import binascii
import rsa

postdata = {
  'entry': 'weibo',
  'gateway': '1',
  'from': '',
  'savestate': '7',
  'userticket': '1',
  'ssosimplelogin': '1',
  'vsnf': '1',
  'vsnval': '',
  'su': '',
  'service': 'miniblog',
  'servertime': '',
  'nonce': '',
  'pwencode': 'rsa2',
  'sp': '',
  'encoding': 'UTF-8',
  'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
  'returntype': 'META'
}

class Weibo():
  def __init__(self):
    # 获取一个保存cookie的对象
    self.cj = cookielib.LWPCookieJar()

    # 将一个保存cookie对象，和一个HTTP的cookie的处理器绑定
    cookie_support = urllib2.HTTPCookieProcessor(self.cj)

    # 创建一个opener，将保存了cookie的http处理器，还有设置一个handler用于处理http的URL的打开
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

    # 将包含了cookie、http处理器、http的handler的资源和urllib2对象板顶在一起
    urllib2.install_opener(opener)

  def _get_servertime(self, username):
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' %username
    data = urllib2.urlopen(url).read()
    p = re.compile('\((.*)\)')
    json_data = p.search(data).group(1)
    data = json.loads(json_data)
    servertime = str(data['servertime'])
    nonce = data['nonce']
    pubkey = data['pubkey']
    rsakv = data['rsakv']
    return servertime, nonce, pubkey, rsakv

  def _get_pwd(self, pwd, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
    pwd = rsa.encrypt(message, key)
    return binascii.b2a_hex(pwd)

  def _get_user(self, username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username

  def login(self, username, pwd):
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
    try:
      servertime, nonce, pubkey, rsakv = self._get_servertime(username)
    except:
      print >> sys.stderr, 'Get severtime error!'
      return None
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['su'] = self._get_user(username)
    postdata['sp'] = self._get_pwd(pwd, servertime, nonce, pubkey)
    postdata['rsakv'] = rsakv
    postdata = urllib.urlencode(postdata)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}

    req = urllib2.Request(
      url=url,
      data=postdata,
      headers=headers
    )

    result = urllib2.urlopen(req)
    text = result.read()
    p = re.compile('location\.replace\([\'|"](.*?)[\'|"]\)')
    try:
      return p.search(text).group(1)
    except:
      return None

if __name__ == '__main__':
  weibo = Weibo()
  # weibo.login('your weibo account', 'your password')
