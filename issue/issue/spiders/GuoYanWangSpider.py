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


class GuoYanWangSpider(scrapy.Spider):
    name = "GuoYanWang"
    urls = []
    subject = ""

    def __init__(self, url=None, pages=None, subject=None, *args, **kwargs):
        super(GuoYanWangSpider, self).__init__(*args, **kwargs)
        self.urls = self.getUrls(url, pages)
        self.subject = subject
        print self.subject + "\t" + str(self.urls)

    def getUrls(self, url, pages):
        result = []
        for i in range(int(pages)):
            curpage = i + 1
            searchUrl = url + str(curpage)
            result.append(searchUrl)
        return result

    def start_requests(self):
        urls = self.urls
        subject = self.subject
        source = '国研网'
        source_url = 'http://www.drcnet.com.cn/'
        for url in urls:
            meta = {'source': source, 'source_url': source_url, 'search_url': url, 'subject': subject}
            yield Request(url, self.parse, meta=meta)

    def parse(self, response):
        meta = {'source': response.meta['source'], 'source_url': response.meta['source_url'],
                'search_url': response.meta['search_url'], 'subject': response.meta['subject']}
        searchresults = response.xpath(".//div[@class='pub_content']")
        for item in searchresults:
            access_url = item.xpath(".//li/a/@href").extract_first()
            title = item.xpath(".//li/a/@title").extract_first()
            meta['access_url'] = access_url
            meta['pdf_url'] = access_url + "&downloadflag=down"
            meta['title'] = title
            keyWords = item.xpath(".//div[@class='mt10']/span/text()").extract_first()
            release_date = item.xpath(".//li/span[@class='date de-date']/span/text()").extract_first()
            meta['release_date'] = release_date
            meta['keywords'] = keyWords.replace('，', ';')
            author_source = item.xpath(".//ul[@class='extra clearfix clear']/li")
            author = ""
            collection = ""
            for elem in author_source:
                author_sourceStr = ("").join(elem.xpath(".//text()").extract())
                if author_sourceStr.__contains__("⊙作者:"):
                    author = author_sourceStr
                else:
                    collection = author_sourceStr
            meta['author'] = author
            meta["collection"] = collection
            print "author:" + author
            print "collection:" + collection
            print title
            print release_date
            yield response.follow(access_url, self.parse_issue, meta=meta)

    def parse_issue(self, response):
        result = {'source': response.meta['source'],
                  'source_url': response.meta['source_url'],
                  'search_url': response.meta['search_url'],
                  'subject': response.meta['subject'],
                  'title': response.meta['title'],
                  'author': response.meta['author'],
                  'collection': response.meta['collection'],
                  'keywords': response.meta['keywords'],
                  'access_url': response.meta['access_url'],
                  'pdf_url': response.meta['pdf_url'],
                  'release_date': response.meta['release_date'],
                  }
        abstract = "".join(response.xpath(".//div[@id='docSummary']//text()").extract())
        editor =  "".join(response.xpath(".//span[@id='docEditor']//text()").extract())
        result['abstract'] = abstract
        result['editor'] = editor
        yield result
