# -*- coding: utf-8 -*-
import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http.request import Request

import urlparse
import re

"""
1. oxfordjounal本来已经配置了portia爬取的，但是爬到一半(4w个)失败了。
所以决定用scrapy把所有详情页的url爬取下来。2018.03.21
"""
class OxfordSpider(CrawlSpider):
    name = 'oxford'

    #def __init__(self, url_file=None, *args, **kwargs):
    #    self.url_file = url_file

    f = open("/Users/baidu/work/simplehttp/oxfordjournals.url")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()

    rules = (
        Rule(LinkExtractor(allow=('academic.oup.com/[^/]+/issue/\d+/\d+$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=(
            'academic.oup.com/[^/]+/issue-archive/201[5-8]+$',
        ))),
    )

    def parse_issue(self, response):
        volumn_issue = response.xpath(".//div[@class='issue-info-pub']/text()").extract_first().strip()
        sections = response.xpath("//div[@class='section-container']")
        journal = response.xpath("//div[@class='center-inner-row']/a/@href").extract_first()
        for section in sections:
            for article in section.xpath(".//div[@class='al-article-items']"):
                url = urlparse.urljoin(response.url, article.xpath(".//h5/a/@href").extract_first())
                yield {
                    "url" : url,
                    "volume_issue" : volumn_issue,
                    "journal" : journal
                }


