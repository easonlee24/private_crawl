#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class WorldBankAuthorSpider(scrapy.Spider):
    name = "worldbankAuthor"
    urls = []

    def __init__(self, url_file=None, *args, **kwargs):
        super(WorldBankAuthorSpider, self).__init__(*args, **kwargs)
        self.urls = self.readText(url_file)
        print self.urls

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        urls = []
        while len(line) > 0:
            print line
            url = line.strip()
            urls.append(url)
            line = f.readline().strip()
        f.close()
        return urls

    def start_requests(self):
        urls = self.urls
        for url in urls:
            meta = {'url': url}
            yield Request(url, self.parse, meta=meta)

    def parse(self, response):
        url = response.meta['url']
        authorList = response.xpath(".//a[@class='entryAuthor']/text()").extract()
        author = "ERROR"
        if len(authorList) > 0:
            author = (";").join(authorList)
        yield {
            "url": url,
            "author": author
        }
