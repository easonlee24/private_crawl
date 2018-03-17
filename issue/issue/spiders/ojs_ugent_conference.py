#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class ojs_ugent_conferenceSpider(scrapy.Spider):
    name = "ojs_ugent_conference"
    infos = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(ojs_ugent_conferenceSpider, self).__init__(*args, **kwargs)
        self.infos = self.readText(urlPath)
        print self.infos

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        infos = []
        while len(line) > 0:
            infolist = line.strip().split("\t")
            infodic = {}
            infodic['id'] = infolist[0]
            infodic['source'] = infolist[1]
            infodic['source_url'] = infolist[2]
            infodic['conferenceUrl'] = infolist[3]
            infodic['conference_name'] = infolist[4]
            infodic['conference_year'] = infolist[5]
            infodic['volume'] = infolist[6]
            infodic['search_url'] = infolist[7]
            infos.append(infodic)
            line = f.readline().strip()
        f.close()
        return infos

    def start_requests(self):
        infos = self.infos
        for info in infos:
            meta = info
            url = info['search_url']
            yield Request(url, self.parse, meta=meta)

    def parse(self, response):
        article_xpath=response.xpath(".//table[@class='tocArticle']")
        for elem in article_xpath:
            result = {'id': response.meta['id'], 'source': response.meta['source'],
                      'source_url': response.meta['source_url'],
                      'conferenceUrl': response.meta['conferenceUrl'],
                      'conference_name': response.meta['conference_name'],
                      'conference_year': response.meta['conference_year'],
                      'volume': response.meta['volume'],
                      'search_url': response.meta['search_url']}
            title = elem.xpath(".//td[@class='tocArticleTitleAuthors']/div[@class='tocTitle']/text()").extract_first().strip()
            author = elem.xpath(".//td[@class='tocArticleTitleAuthors']/div[@class='tocAuthors']/text()").extract_first().strip()
            pdf_url = elem.xpath(".//td[@class='tocArticleGalleysPages']/div[@class='tocGalleys']/a/@href").extract_first().strip().replace('/view/','/download/')
            result['title'] = title
            result['author'] = author
            result['pdf_url'] = pdf_url
            yield result

