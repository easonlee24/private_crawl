#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class econPaper_link2urlV2(scrapy.Spider):
    name = "econPaper_link2urlV2"
    urls = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(econPaper_link2urlV2, self).__init__(*args, **kwargs)
        self.urls = self.readText(urlPath)

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        result = []
        while len(line) > 0:
            accsse_url = line.split("|")[1]
            result.append(accsse_url)
            line = f.readline().strip()
        f.close()
        return result

    def start_requests(self):
        urls = self.urls
        for url in urls:
            meta = {'accsse_url': url}
            yield Request(url, self.parse, meta=meta)

    def parse(self, response):
        meta = {'accsse_url': response.meta['accsse_url']}
        p_xpath = response.xpath(".//div[@class='bodytext']/p")
        pdf_urlxpath = [elem for elem in p_xpath if elem.xpath("./b/text()").extract().__contains__("Downloads:")]
        if len(pdf_urlxpath) != 0:
            pdf_urls = pdf_urlxpath[0].xpath("./a")
            for item in pdf_urls:
                desc = item.xpath("following-sibling::text()[1]").extract_first().strip()
                link = urlparse.urljoin(response.url, item.xpath("@href").extract_first().strip())
                meta['pdflink_dec'] = desc
                yield response.follow(link, self.parse_url, meta=meta)

    def parse_url(self, response):
        meta = {'accsse_url': response.meta['accsse_url'], 'pdflink_dec': response.meta['pdflink_dec']}
        pdf_url = response.url
        meta['pdf_url'] = pdf_url
        yield meta
