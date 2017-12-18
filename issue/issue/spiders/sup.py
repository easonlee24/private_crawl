# -*- coding: utf-8 -*-
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json

"""
This sipder will continue to crawl some fields that:
1. cannot easy crawled by portia
2. miss fields 
"""
class SupSpider(scrapy.Spider):
    name = 'sup'

    def __init__(self, url_file=None):
        self.url_file = url_file

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                issue_url = line.strip()

                print "start to crawl: %s" % issue_url
                yield Request(issue_url, self.sage_sub, dont_filter=True)

    """
    Sage质检结果，发现少了一些字段
    """
    def sage_sub(self, response):
        publish_year = Utils.extract_with_xpath(response, "//div[@class='articleJournalNavTitle']/text()").split(',')
        keywords = ",".join(response.xpath("//div[@class='hlFld-KeywordText']/kwd-group/a/text()").extract())
        author = ",".join(response.xpath("//div[@class='authors']//div[@class='header']/a[@class='entryAuthor']/text()").extract())
        if author == "":
            author = ",".join(response.xpath("//div[@class='authors']//span[@class='contrib']/a[@class='entryAuthor']/text()").extract())

        publish_date = Utils.extract_all_with_xpath(response, "//span[@class='publicationContentEpubDate dates']/text()")
        abstract = ",".join(response.xpath("//div[@class='abstractSection abstractInFull']/p/text()").extract())
        source = 'sage'
        source_url = 'http://journals.sagepub.com/'
        acquisition_time = Utils.current_time()
        if len(publish_year)!= 3:
            raise Exception("cannot find publish_year for %s" % response.url)
        else:
            publish_year = publish_year[-1]

        yield {
            'publish_year': publish_year,
            'keywords': keywords,
            'author': author,
            'publish_date': publish_date,
            'abstract': abstract,
            'source': source,
            'source_url': source_url,
            'acquisition_time': acquisition_time,
            'url': response.url
        }
