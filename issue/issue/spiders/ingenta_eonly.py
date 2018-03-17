#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import urlparse
import sys
from scrapy.http.request import Request
import requests

reload(sys)
sys.setdefaultencoding('utf8')


class Ingenta(scrapy.Spider):
    name = "Ingenta"
    urls = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(Ingenta, self).__init__(*args, **kwargs)
        self.urls = self.readText(urlPath)
        print self.urls

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        result = []
        while len(line) > 0:
            result.append(line.strip())
            line = f.readline().strip()
        f.close()
        return result

    def start_requests(self):
        urls = self.urls
        meta = {}
        for item in urls:
            search_url = item.split("\t")[0]
            collection = item.split("\t")[1]
            issn = item.split("\t")[2]
            eissn = item.split("\t")[3]
            meta['search_url'] = search_url
            meta['collection'] = collection
            meta['issn'] = issn
            meta['eissn'] = eissn
            yield Request(search_url, self.parse, meta=meta)

    def parse(self, response):
        meta = {'search_url': response.meta['search_url'],
                'collection': response.meta['collection'],
                'issn': response.meta['issn'],
                'eissn': response.meta['eissn'],
                }
        issue_urls = response.xpath(".//div[@id='Issu']/ul[@class='bobby']//a/@href").extract()
        for url in issue_urls:
            issue_url = urlparse.urljoin(response.url, url.strip())
            meta['issue_url'] = issue_url
            yield response.follow(issue_url, self.parse_issue, meta=meta)

    def parse_issue(self, response):
        meta = {'search_url': response.meta['search_url'],
                'collection': response.meta['collection'],
                'issn': response.meta['issn'],
                'eissn': response.meta['eissn'],
                'issue_url': response.meta['issue_url']
                }

        volume_issue_yearInfo = response.xpath(
            ".//div[@class='heading-macfix']/div[@class='left-col']/text()").extract_first()
        meta['volume_issue_yearInfo'] = volume_issue_yearInfo

        articles_xpath = response.xpath(".//div[@class='greybg']/div[@class='data']")
        for elem in articles_xpath:
            access_url = urlparse.urljoin(response.url,
                                          elem.xpath(".//div[@class='ie5searchwrap']//a/@href").extract_first().strip())
            title = elem.xpath(".//div[@class='ie5searchwrap']//a/@title").extract_first().strip()
            pages = elem.xpath(".//div[@class='ie5searchwrap']//br[1]").xpath(
                "following-sibling::text()[1]").extract_first().strip()
            meta['access_url'] = access_url
            meta['pages'] = pages
            meta['title'] = title
            yield response.follow(access_url, self.parse_article, meta=meta)

    def parse_article(self, response):
        meta = {'search_url': response.meta['search_url'],
                'collection': response.meta['collection'],
                'issn': response.meta['issn'],
                'eissn': response.meta['eissn'],
                'issue_url': response.meta['issue_url'],
                'volume_issue_yearInfo': response.meta['volume_issue_yearInfo'],
                'access_url': response.meta['access_url'],
                'pages': response.meta['pages'],
                'title': response.meta['title']
                }
        abstract = "".join(response.xpath(".//div[@id='Abst']//text()").extract()).strip()
        # if abstract.__contains__("No Abstract."):
        #     abstract="&"
        meta['abstract'] = abstract
        infoArticlexpath = response.xpath(".//div[@id='infoArticle']/div[@class='supMetaData']/p")

        authorxpath = [elem for elem in infoArticlexpath if
                       elem.xpath("./strong/text()").extract().__contains__("Authors: ")]
        author = "&"
        if len(authorxpath) != 0:
            author = ";".join(authorxpath[0].xpath(".//a/text()").extract())

        doixpath = [elem for elem in infoArticlexpath if
                    elem.xpath("./strong/text()").extract().__contains__("DOI:")]
        doi = "&"
        if len(doixpath) != 0:
            doi = ";".join(doixpath[0].xpath(".//a/text()").extract())

        meta['author'] = author
        meta['doi'] = doi
        yield meta
