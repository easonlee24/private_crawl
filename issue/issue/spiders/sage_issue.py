# -*- coding: utf-8 -*-
import scrapy
import urlparse
from scrapy.http.request import Request
from utils import Utils


"""
sage的数据库和期刊类爬取方式还不太一样
"""
class SageIssueSpider(scrapy.Spider):
    name = 'sage_issue'
    start_urls = [
      #第一次新增
      #'http://journals.sagepub.com/articles/vrt',
      #'http://journals.sagepub.com/articles/cbx',
      #'http://journals.sagepub.com/articles/bds',

      #第二次新增
      #'http://journals.sagepub.com/articles/asn',
      #v'http://journals.sagepub.com/articles/cld',
      #'http://journals.sagepub.com/articles/jor',
      #'http://journals.sagepub.com/articles/iem',

      'http://journals.sagepub.com/articles/oag',
    ]

    def parse(self, response):
      page_info = response.xpath("//div[@class='paginationStatus']/span/text()").extract()[-1]
      print "page_info %s" % page_info
      total_num = int(Utils.regex_extract(page_info, "of (\d+)"))
      articles = response.xpath("//ol[@class='search-results']/li")
      for article in articles:
        url = article.xpath(".//a[@data-item-name='click-article-title']/@href").extract_first()
        url = urlparse.urljoin(response.url, url)
        yield {
          "url": url,
          "from_url" : response.url,
        }

      page_num = int((total_num -1)/ 20) + 1
      print "real page %d" % page_num

      if "page" in response.meta:
        print "page in response meta :%s" % response.meta["page"]
        return

      page_index = 0
      while page_index < page_num:
        meta = {"page" : page_index}
        page_url = "%s?pageSize=20&startPage=%d" % (response.url, page_index)
        print "follow page :%d" % page_index
        yield response.follow(page_url, self.parse, meta = meta)
        page_index = page_index + 1
      
