#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
import re
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class e3s_conferenceSpider(scrapy.Spider):
    name = "e3s_conference"
    infos = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(e3s_conferenceSpider, self).__init__(*args, **kwargs)
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
        searchresults = response.xpath(".//a[@class='article_title']/@href").extract()
        for item in searchresults:
            access_url = urlparse.urljoin(response.url, item.strip())
            meta['access_url'] = access_url
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
                  'access_url': response.meta['access_url']}
        tableinfo = response.xpath(".//div[@class='summary ']//tr")
        for item in tableinfo:
            namelist = item.xpath("./th/text()")
            if len(namelist) == 0:
                continue
            name = item.xpath("./th/text()").extract_first().strip()
            info = item.xpath(".//td//text()").extract()
            c = [elem for elem in info if len(elem.strip()) > 0]
            d = "".join(c).strip().split("\t")
            n = "\t".join([elem.strip() for elem in d if len(elem.strip()) > 0])
            result[name] = n

        title = "".join(response.xpath(
            ".//div[@id='contenu-min']/div[@id='head']/h2[@class='title']/text()").extract()).strip()
        result['title'] = title

        downloadlist = response.xpath(".//div[@class='article_doc']//@href").extract()
        pdf_url = [urlparse.urljoin(response.url, elem.strip()) for elem in downloadlist if
                   str(elem).__contains__(".pdf")]
        result['pdf_url'] = "".join(pdf_url)

        abstractxpath = response.xpath(".//div[@id='contenu-min']/div[@id='head']/p[@class='no_abs']")
        abstract = "wrong"
        # preceding-sibling
        if len(abstractxpath) == 0:
            abstract = "".join(response.xpath(".//div[@id='contenu-min']/div[@id='head']/p[@class='bold']").xpath(
                "following-sibling::p[1]/text()").extract())
        result['abstract'] = abstract

        authorxpath = response.xpath(".//div[@id='contenu-min']/div[@id='head']/div[@class='article-authors']")
        author = []
        author_sup = []
        author_affiliation = []
        if len(authorxpath) > 0:
            authors_xpath = authorxpath.xpath(".//span[@class='author']")
            for author_xpth in authors_xpath:
                author.append(author_xpth.xpath("./text()").extract_first().strip())
                author_sup.append("".join(author_xpth.xpath("following-sibling::sup[1]/text()").extract()))
            author_sup = [elem for elem in author_sup if elem != '']
            affiliationxpath = response.xpath(".//div[@id='contenu-min']/div[@id='head']/p[@class='aff']")
            pattern = re.compile(r'(\d+)')
            if len(author_sup) > 0 and len([elem for elem in author_sup if len(pattern.findall(elem)) > 0]) > 0:
                affiliation_sup = affiliationxpath.xpath(".//sup")
                author_affiliation_2 = []
                for elem in affiliation_sup:
                    # sup = elem.xpath("./text()").extract_first().strip()
                    affiliation = elem.xpath("following-sibling::text()[1]").extract_first().strip()
                    # author_affiliation_2.append(sup + "@@" + affiliation)
                    author_affiliation_2.append(affiliation)
                author_affiliation = author_affiliation_2
            else:
                if len(affiliationxpath.xpath(".//text()")) > 0:
                    author_affiliation = [affiliationxpath.xpath(".//text()").extract_first().strip()]
        result["author"] = author
        result["author_sup"] = author_sup
        result["author_affiliation"] = author_affiliation
        keywordslist = response.xpath(".//div[@class='kword']//text()").extract()
        keywords = "".join(keywordslist)
        result["keywords"] = keywords.replace("Key words: ","")
        yield result
