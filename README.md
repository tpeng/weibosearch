WeiboSearch
===================
A distributed Sina Weibo Search spider base on Scrapy and Redis.

tpeng <pengtaoo@gmail.com>

## Usage
1. put your keywords in items.txt
2. scrapy crawl weibosearch -a username=your_weibo_account:your_weibo_pw
3. add another spider with *scrapy crawl weibosearch -a username=another_weibo_account:another_weibo_pw*

## How to install

### Basic Tools
1. apt-get install python-setuptools
2. apt-get install python-dev
3. apt-get install libxml2-dev libxslt-dev
4. apt-get install mysql-server redis-server

### PyQuery
#### Windows
1. install [mingw32](http://www.mingw.org/)
2. add mingw32 bin to the path (e.g. c:\mingw32\bin)
3. create distutils.cfg under PYTHON\lib\distutils and add

    [build]
    compiler=mingw32

4. remove *-mno-cygwin* from PYTHON\lib\distutilscygwinccompiler.py
5. install lxml
4. easy_install pyquery

### Scrapy
1. easy_install scrapy <https://github.com/andymccurdy/redis-py>

### MySQL-Python
#### Windows
1. http://www.codegood.com/downloads

#### Linux
1. sudo apt-get install python-mysqldb

### Redis
1. easy_install redis