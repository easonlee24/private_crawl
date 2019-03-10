# -*- coding: utf-8 -*-
import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http.request import Request

import urlparse
import re

"""
决定用scrapy把所有详情页的url爬取下来。2018.03.27
"""
class BmjUrlSpider(CrawlSpider):
    name = 'bmj_url'

    #def __init__(self, url_file=None, *args, **kwargs):
    #    self.url_file = url_file

    #f = open("/Users/baidu/work/simplehttp/bmj.url")
    f = open("/Users/baidu/work/private_crawl/issue/issue/OA_20180809/bmj_miss_url")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()

    #rules = (
    #    Rule(LinkExtractor(allow=('bmj.com/content/\d+/\d+$', )), callback='parse_issue'),
    #    Rule(LinkExtractor(allow=('bmj.com/content/\d+/\w+\?page=\d+$', )), callback='parse_issue'),
    #    #Rule(LinkExtractor(allow=(
    #    #    'bmj.com/content/by/year/201[5-8]+$',
    #    #))),
    #)

    def parse(self, response):
        titles = response.xpath("//div[@class='highwire-list']//li")
        if len(titles) == 0:
            titles = response.xpath("//div[@class='issue-toc']//ul[@class='toc-section']/li")

        for title in titles:
            release_date = "".join(title.xpath(".//a[@class='highwire-cite-linked-title']/../text()").extract()).strip()
            release_year = release_date.split(",")[-1]
            url = title.xpath(".//a[@class='highwire-cite-linked-title']/@href").extract_first()
            url = urlparse.urljoin(response.url, url)
            yield {
                "url" : url,
                "release_date" : release_date,
                "release_year" : release_year,
                "from_url": response.url,
            }

        if "page" not in response.meta:
            #处理分页的情况
            last_page = response.xpath("//li[@class='pager-last last']/a/@href").extract_first()
            try:
                page_num = int(last_page.split("=")[-1])
            except Exception as e:
                page_num = 1
            page_index = 2
            while page_index <= page_num:
                meta = {"page": page_index}
                page_url = "%s?page=%d" % (response.url, page_index)
                yield response.follow(page_url, self.parse, meta = meta)
                page_index = page_index + 1
