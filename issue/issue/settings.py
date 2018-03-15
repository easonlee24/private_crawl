# -*- coding: utf-8 -*-

# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'issue'

SPIDER_MODULES = ['issue.spiders']
NEWSPIDER_MODULE = 'issue.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 5
## The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 5
#CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'tutorial.middlewares.TutorialSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'tutorial.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'tutorial.pipelines.TutorialPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

FEED_EXPORT_ENCODING = 'utf-8'
COOKIES_ENABLES = False
PROXIES = [
    {'ip_port': '14.29.47.90:3128', 'user_pass': None},
    {'ip_port': '211.159.177.212:3128', 'user_pass': None},
    {'ip_port': '111.230.165.16:3128', 'user_pass': None},
    {'ip_port': '120.26.14.14:3128', 'user_pass': None},
    {'ip_port': '59.67.152.230:3128', 'user_pass': None},
    {'ip_port': '119.28.152.208:80', 'user_pass': None},
    {'ip_port': '122.72.18.34:80', 'user_pass': None},
    {'ip_port': '122.72.18.35:80', 'user_pass': None},
    {'ip_port': '219.135.164.245:3128', 'user_pass': None},
    {'ip_port': '114.215.95.188:3128', 'user_pass': None},
    {'ip_port': '101.132.121.157:9000', 'user_pass': None},
    {'ip_port': '139.129.166.68:3128', 'user_pass': None},
    {'ip_port': '203.174.112.13:3128', 'user_pass': None},
    {'ip_port': '118.212.137.135:31288', 'user_pass': None},
    {'ip_port': '222.186.45.117:55336', 'user_pass': None},
    {'ip_port': '27.44.162.135:9999', 'user_pass': None},
    {'ip_port': '218.20.54.152:9797', 'user_pass': None},
]

#取消默认的useragent,使用新的useragent
DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddleware.useragent.UserAgentMiddleware' : None,
        'scrapy.downloadermiddleware.redirect.RedirectMiddleware' : None,
        'issue.rotate_useragent.RotateUserAgentMiddleware' : 500,
        'issue.custom_redirect.CustomRedirectMiddleware' : 600,
        #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
        #'issue.rotate_useragent.ProxyMiddleware': 100,
}
