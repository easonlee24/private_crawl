#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class econPaper_link2url(scrapy.Spider):
    name = "econPaper_link2url"
    urls = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(econPaper_link2url, self).__init__(*args, **kwargs)
        self.urls = self.readText(urlPath)

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        result = []
        while len(line) > 0:
            accsse_url = line.split("|")[1]
            for elem in line.split("|")[0].split("$$"):
                result.append(elem + "|" + accsse_url)
            line = f.readline().strip()
        f.close()
        return result

    def start_requests(self):
        urls = self.urls
        for url in urls:
            accsse_url = url.split("|")[1]
            meta = {'accsse_url': accsse_url, 'pdflink_dec': url.split("|")[0].split("@@")[0]}
            pdflink = url.split("|")[0].split("@@")[1]
            yield Request(pdflink, self.parse, meta=meta)

    def parse(self, response):
        meta = {'accsse_url': response.meta['accsse_url'], 'pdflink_dec': response.meta['pdflink_dec']}
        pdf_url = response.url
        meta['pdf_url'] = pdf_url
        yield meta
