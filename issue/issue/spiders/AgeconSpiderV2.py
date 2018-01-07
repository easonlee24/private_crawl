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


class AgeconSpiderV2(scrapy.Spider):
    name = "ageconV2"
    urls = []

    def __init__(self, url_file=None, *args, **kwargs):
        super(AgeconSpiderV2, self).__init__(*args, **kwargs)
        self.urls = self.readText(url_file)
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
        for url in urls:
            meta = {'search_url': url}
            yield Request(url, self.parse, meta=meta)
            # meta = {'search_url': url, 'article_url': url}
            # yield Request(url, self.parse_issue, meta=meta)

    def parse(self, response):
        meta = {'search_url': response.meta['search_url']}
        allurls = response.xpath(".//a/@href").extract()
        detailUrls = [elem for elem in allurls if str(elem).__contains__("record") and str(elem).__contains__("?ln=en")]
        for url in detailUrls:
            detailUrl = urlparse.urljoin(response.url, url.strip())
            meta['article_url'] = detailUrl
            yield response.follow(detailUrl, self.parse_issue, meta=meta)

    def parse_issue(self, response):
        result = {}
        search_url = response.meta['search_url']
        article_url = response.meta['article_url']
        result['search_url'] = search_url
        result['article_url'] = article_url
        titleList = response.xpath(".//h2[@class='record-title']/text()").extract()
        title = "wrong"
        if len(titleList) != 0:
            title = "".join(titleList).strip()
        result['title'] = title
        authorsList = response.xpath(".//div[@class='record-detail-meta record-authors']/a/text()").extract()
        author = "wrong"
        if len(authorsList) != 0:
            author = ",".join(authorsList).strip()
        result['author'] = author
        abstractList = response.xpath(".//p[@class='record-abstract']/text()").extract()
        abstract = "wrong"
        if len(abstractList) != 0:
            abstract = "".join(abstractList).strip()
        result['abstract'] = abstract
        keys = response.xpath(".//div[@class='record-meta-key']/text()").extract()
        valueSelectors = response.xpath(".//div[@class='record-meta-value']")
        keys_valueSelectors = zip(keys, valueSelectors)
        for key, valueSelector in keys_valueSelectors:
            key = key.strip().replace(":", "")
            if key.__contains__("Keywords") or key.__contains__("Record appears in"):
                splitStr = ""
            else:
                splitStr = ";"
            valueList = valueSelector.xpath(".//text()").extract()
            if len(valueList) > 1:
                value = splitStr.join(valueList)
            else:
                value = valueList[0]
            result[key] = value
        pdflist = response.xpath(".//i[@class='fa fa-cloud-download']").xpath("following-sibling::a/@href").extract()
        pdf_url = "wrong"
        filePath = "wrong"
        if len(pdflist) != 0:
            pdf_url = urlparse.urljoin(response.url, pdflist[0].strip())
            tmp = pdf_url.split(".")
            pdf_name = str(response.url).split("/")
            filePath = "/Users/chenlu/Downloads/wangting/agecon_pdf/" + pdf_name[len(pdf_name) - 1] + "." + tmp[
                len(tmp) - 1]
            # self.downloadPDF(pdf_url, filePath)
        result['pdf_url'] = pdf_url
        result['filePath'] = filePath
        yield result

    def downloadPDF(self, pdf_url, filePath):
        # file_url = "http://ageconsearch.umn.edu/record/6074/files/454427.pdf"
        r = requests.get(pdf_url, stream=True)
        with open(filePath, "wb") as pdf:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)
            print filePath + " successful!!!"
