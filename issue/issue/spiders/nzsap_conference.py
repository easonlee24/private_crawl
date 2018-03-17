#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
import re
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class nzsap_conferenceSpider(scrapy.Spider):
    name = "nzsap_conference"
    infos = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(nzsap_conferenceSpider, self).__init__(*args, **kwargs)
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
        meta = {'id': response.meta['id'], 'source': response.meta['source'], 'source_url': response.meta['source_url'],
                'conferenceUrl': response.meta['conferenceUrl'], 'conference_name': response.meta['conference_name'],
                'conference_year': response.meta['conference_year'],
                'volume': response.meta['volume'],
                'search_url': response.meta['search_url']}
        searchresults = response.xpath(".//div[@class='view-content']/div[contains(@class, 'views-row views-row-')]")
        for item in searchresults:
            title_url = item.xpath(".//span[@class='biblio-title']/a")
            title = title_url.xpath("text()").extract_first()
            access_url = urlparse.urljoin(response.url, title_url.xpath("@href").extract_first())
            authors = ";".join(item.xpath(".//span[@class='biblio-authors']//a/text()").extract())
            volume = item.xpath(".//a[contains(@href, '/view/biblio/volume')]/text()").extract_first()
            pdf_url = [elem.xpath("@href").extract_first() for elem in item.xpath(".//div[@class='biblio-entry']/a") if
                       elem.xpath("text()").extract_first().__contains__("Full PDF")][0]
            meta['access_url'] = access_url
            meta['title'] = title
            meta['authors'] = authors
            meta['volume'] = volume
            meta['pdf_url'] = pdf_url
            yield response.follow(access_url, self.parse_issue, meta=meta)

    def parse_issue(self, response):
        result = {'id': response.meta['id'],
                  'source': response.meta['source'],
                  'source_url': response.meta['source_url'],
                  'conferenceUrl': response.meta['conferenceUrl'],
                  'conference_name': response.meta['conference_name'],
                  'conference_year': response.meta['conference_year'],
                  'volume': response.meta['volume'],
                  'search_url': response.meta['search_url'],
                  'access_url': response.meta['access_url'],
                  'title': response.meta['title'],
                  'authors': response.meta['authors'],
                  'volume': response.meta['volume'],
                  'pdf_url': response.meta['pdf_url']
                  }
        conference_name = response.xpath(".//div[@class='infobox-inner']/h5/i/text()").extract_first()
        abstract_xpath = response.xpath(".//div[@class='infobox-inner']/h5[1]/text()").extract()
        abstract = "".join(abstract_xpath)
        if len(response.xpath(".//div[@class='infobox-inner']/h5[1]/text()").extract()) == 0:
            abstract = "".join(response.xpath(".//div[@class='infobox-inner']/p//text()").extract())
        result['abstract'] = abstract
        result['conference_name'] = conference_name
        pattern = re.compile(r'(\d+\-\d+)')
        pageslist=pattern.findall("".join(response.xpath(".//div[@class='infobox-inner']/h5[2]/text()").extract()))
        pages="wrong"
        if len(pageslist) !=0 :
            pages = pageslist[0]
        result['pages'] = pages
        pattern_year = re.compile(r'(\d{4}$)')
        conference_yearlist=pattern_year.findall("".join(response.xpath(".//div[@class='infobox-inner']/h5[2]/text()").extract()))
        conference_year = "wrong"
        if len(pageslist) != 0:
            conference_year = conference_yearlist[0]
        result['conference_year'] = conference_year
        yield result
