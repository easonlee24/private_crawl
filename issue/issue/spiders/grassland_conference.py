#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class grassland_conferenceSpider(scrapy.Spider):
    name = "grassland_conference"
    infos = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(grassland_conferenceSpider, self).__init__(*args, **kwargs)
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
        urls = response.xpath(".//h3//a/@href").extract()
        tags = ["pubdesc_" + elem.split("_")[2].replace(".pdf", "") for elem in urls if elem.__contains__(".pdf")]
        for elem in set(tags):
            result = {'id': response.meta['id'], 'source': response.meta['source'],
                      'source_url': response.meta['source_url'],
                      'conferenceUrl': response.meta['conferenceUrl'],
                      'conference_name': response.meta['conference_name'],
                      'conference_year': response.meta['conference_year'],
                      'volume': response.meta['volume'],
                      'search_url': response.meta['search_url']}
            id = elem.split("_")[1]
            tag = ".//p[@id='" + elem + "']"
            abstract_xpath = response.xpath(tag)
            abstract = abstract_xpath.xpath("text()").extract_first()
            title = abstract_xpath.xpath("preceding-sibling::h2[1]/text()").extract_first()
            author = abstract_xpath.xpath("preceding-sibling::h2[1]/em/text()").extract_first()
            pdf_url = "https://www.grassland.org.nz/publications/nzgrassland_publication_" + id + ".pdf"
            result['title']=title
            result['author'] = author
            result['abstract'] = abstract
            result['pdf_url'] = pdf_url
            yield result


