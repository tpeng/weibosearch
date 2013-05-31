WeiboSearch
===================
A distributed Sina Weibo Search spider base on Scrapy and Redis.

tpeng <pengtaoo@gmail.com>

## Installation
    $ sudo apt-get install mysql-server
    $ sudo apt-get install redis-server
    $ sudo apt-get install python-mysqldb
    $ sudo pip install -r requirements.txt

## Usage
1. put your keywords in items.txt
2. `scrapy crawl weibosearch -a username=your_weibo_account -a password=your_weibo_password`
3. add another spider with *scrapy crawl weibosearch -a username=another_weibo_account -a password=another_weibo_password*

or
1. `scrapy crawl weibosearch -a username=your_weibo_account -a password=your_weibo_password -a savedb=False` to avoid save to
mysql db. (easier for experiment)
