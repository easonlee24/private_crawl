# -*- coding: utf-8 -*-
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json

"""
输入期刊url，得到详情页的url
1. cannot easy crawled by portia
2. miss fields 
"""
class ArticleUrlSpider(scrapy.Spider):
    name = 'article_url'
    def __init__(self, url_file=None, meta_file = None):
        self.url_file = url_file
        self.crawl_urls = []
        if meta_file:
            with open(meta_file, "rb") as f:
                for line in f:
                    try:
                      json_data = json.loads(line.strip())
                      issue_url = json_data["access_url"]
                    except Exception:
                      continue
                    self.crawl_urls.append(issue_url)

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                try:
                    json_data = json.loads(line.strip())
                    issue_url = json_data["access_url"]
                except Exception:
                    issue_url = line.strip()

                if issue_url in self.crawl_urls:
                    print "filter url: %s" % issue_url
                    continue

                yield Request(issue_url, self.aosis, dont_filter=True)

                if issue_url.find("mdpi.com") != -1:
                    yield Request(issue_url, self.mdpi, dont_filter=True)
                elif issue_url.find("sagepub") != -1:
                    yield Request(issue_url, self.sage, dont_filter=True)
                elif issue_url.find(".za") != -1 or issue_url.find(".org") != -1:
                    yield Request(issue_url, self.aosis, dont_filter=True)
                elif issue_url.find("karger") != -1:
                    yield Request(issue_url, self.karger, dont_filter=True)

    def aosis(self, response):
        urls = response.xpath("//div[@class='article-meta']/a/@href").extract()
        if len(urls) == 0:
            urls = response.xpath("//div[@class='title']/a/@href").extract()
            if len(urls) == 0:
                urls = response.xpath("//div[@class='tocTitle']/a/@href").extract()
            
        for url in urls:
            yield {
                "journal_url": response.url,
                "article_url": urlparse.urljoin(response.url, url)
            }

    def mdpi(self, response):
        urls = response.xpath("//a[@class='title-link']/@href").extract()
        for url in urls:
            yield {
                "journal_url": response.url,
                "article_url": urlparse.urljoin(response.url, url)
            }

    def sage(self, response):
        urls = response.xpath("//a[@data-item-name='click-article-title']/@href").extract()
        for url in urls:
            yield {
                "journal_url": response.url,
                "article_url": urlparse.urljoin(response.url, url)
            }

    def karger(self, response):
        urls = response.xpath("//div[@class='issue_liste']//table//h2[@class='abstract']/a/@href").extract()
        for url in urls:
            yield {
                "journal_url": response.url,
                "article_url": urlparse.urljoin(response.url, url)
            }
